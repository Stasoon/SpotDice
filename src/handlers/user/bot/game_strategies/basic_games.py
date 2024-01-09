import asyncio

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from src.database import games, Game, transactions, PlayerScore, User
from src.database.games import game_scores
from src.handlers.user.bot.game_strategies.game_strategy import GameStrategy
from src.keyboards import UserMenuKeyboards, UserBotGameKeyboards
from src.messages import UserPublicGameMessages
from src.misc import GameStatus
from src.utils.choose_game_messages import get_message_instance_by_game_type
from src.utils.game_messages_sender import GameMessageSender
from src.utils.timer import BaseTimer


class GameTimer(BaseTimer):

    def __init__(self, bot: Bot, game: Game, chat_id: int, message_id: int, seconds_expiry: int, text_template: str):
        super().__init__(chat_id, message_id, seconds_expiry)

        self.bot = bot
        self.game = game
        self.template = text_template

    @classmethod
    async def stop(cls, bot: Bot, chat_id: int):
        try:
            timer = await super(GameTimer, cls).stop(chat_id)
            await bot.delete_message(chat_id=timer.chat_id, message_id=timer.message_id)
        except Exception:
            pass

    async def make_tick(self):
        await super(GameTimer, self).make_tick()

        try:
            await self.bot.edit_message_text(
                chat_id=self.timer.chat_id,
                message_id=self.timer.message_id,
                text=self.template.format(str(self))
            )
        except Exception:
            return

    async def on_time_left(self):
        try:
            await self.bot.delete_message(chat_id=self.timer.chat_id, message_id=self.timer.message_id)
        except TelegramBadRequest:
            pass

        await self.bot.send_message(chat_id=self.timer.chat_id, text="Время на ход вышло!")
        await game_scores.add_player_move_if_not_moved(self.game, self.timer.chat_id, move_value=0)

        if await game_scores.is_all_players_moved(self.game):
            await BasicGameStrategy.finish_game(self.bot, self.game)

        await self.timer.delete()


class BasicGameStrategy(GameStrategy):

    @staticmethod
    async def start_game(bot: Bot, game: Game):
        time_on_move = 10*60
        msg_instance = get_message_instance_by_game_type(game_type=game.game_type)
        player_ids = await games.get_player_ids_of_game(game)

        text = msg_instance.get_game_started()
        counter_text = "⏱ Время на ход: {0}"
        markup = UserBotGameKeyboards.get_dice_kb(game.game_type.value)

        timers = []

        for player_id in player_ids:
            await bot.send_message(chat_id=player_id, text=text, reply_markup=markup)
            counter_msg = await bot.send_message(
                chat_id=player_id, text=counter_text.format(GameTimer.format_seconds_to_time(time_on_move))
            )

            timer = GameTimer(
                bot=bot, game=game,
                chat_id=player_id, message_id=counter_msg.message_id,
                seconds_expiry=time_on_move, text_template=counter_text,
            )

            # Создаем задачу для таймера и добавляем ее в список
            timers.append(asyncio.create_task(timer.start()))

        await asyncio.gather(*timers)

    @staticmethod
    async def __make_refund_for_tie(game: Game, game_moves: list[PlayerScore]) -> None:
        # Возвращаем деньги участникам
        for move in game_moves:
            await transactions.make_bet_refund(game=game, player_id=move.player.telegram_id, amount=game.bet)

    @staticmethod
    async def __accrue_players_winnings_and_get_amount(game: Game, win_coefficient: float, winners: list[User]) -> float:
        # Начисляем выигрыши победителям
        winning_with_commission = None
        for winner in winners:
            winning_with_commission = await transactions.accrue_winnings(
                game_category=game.category, winner_telegram_id=winner.telegram_id,
                amount=game.bet * win_coefficient
            )
        return winning_with_commission

    @staticmethod
    async def send_results(
            bot: Bot, game: Game, game_moves: list[PlayerScore], winning_amount: float, winners: list[User]
    ):
        # Отправляем результат игры в чат
        text = await UserPublicGameMessages.get_game_in_chat_finish(
            game=game, winners=winners, game_moves=game_moves, win_amount=winning_amount
        )
        # Отправляем результат игрокам
        markup = UserMenuKeyboards.get_main_menu()
        await GameMessageSender(bot, game).send(text, markup=markup)

        # Отправляем сообщение о выигрыше / проигрыше
        msg_instance = get_message_instance_by_game_type(game_type=game.game_type)
        tie_text = msg_instance.get_tie() if not winners else None
        for move in game_moves:
            if tie_text:
                message_text = tie_text
            elif move.player in winners:
                message_text = msg_instance.get_player_won(player_name=move.player.name, win_amount=winning_amount)
            else:
                message_text = msg_instance.get_player_loose()

            if message_text:
                await bot.send_message(chat_id=move.player.telegram_id, text=message_text)

    @classmethod
    async def finish_game(cls, bot: Bot, game: Game):
        if game.status == GameStatus.FINISHED:
            return

        win_coefficient = 2

        game_moves = await game_scores.get_game_moves(game)
        await games.finish_game(game)
        await game_scores.delete_game_scores(game)

        winners = []
        winning_with_commission = None
        max_move = max(game_moves, key=lambda move: move.value)

        if all(move.value == max_move.value for move in game_moves):  # Если значения одинаковы (ничья)
            await cls.__make_refund_for_tie(game=game, game_moves=game_moves)
        else:  # значения разные (есть победитель)
            # формируем список победителей
            winners = [await move.player for move in game_moves if move.value == max_move.value]
            # начисляем выигрыши
            winning_with_commission = await cls.__accrue_players_winnings_and_get_amount(
                game=game, winners=winners, win_coefficient=win_coefficient)

        # Ждём окончания анимации
        seconds_to_wait = 3
        await asyncio.sleep(seconds_to_wait)

        await cls.send_results(
            bot=bot, game=game, game_moves=game_moves, winners=winners, winning_amount=winning_with_commission
        )

    @classmethod
    async def handle_game_move_message(cls, message: Message):
        game = await games.get_user_unfinished_game(message.from_user.id)
        if not game:
            return 

        dice = message.dice

        # Если игрок есть в игре и тип эмодзи соответствует
        await GameTimer.stop(bot=message.bot, chat_id=message.from_user.id)
        if game and dice.emoji == game.game_type.value:
            await cls.process_player_move(game, message)

        # если все походили заканчиваем игру
        if len(await game_scores.get_game_moves(game)) == game.max_players:
            await cls.finish_game(bot=message.bot, game=game)

    @classmethod
    async def process_player_move(cls, game: Game, move_message: Message):
        """Обрабатывает ход в игре"""
        game_moves = await game_scores.get_game_moves(game)

        if not await game_scores.is_player_moved(game=game, user_id=move_message.from_user.id):
            for player_id in await games.get_player_ids_of_game(game=game):
                if player_id != move_message.from_user.id:
                    try:
                        await move_message.forward(chat_id=player_id)
                    except Exception:
                        pass

        player_telegram_id = move_message.from_user.id
        dice_value = move_message.dice.value

        # если не все игроки сделали ходы
        if len(game_moves) != game.max_players:
            await game_scores.add_player_move_if_not_moved(
                game=game, player_telegram_id=player_telegram_id, move_value=dice_value
            )

        if len(game_moves) + 1 != game.max_players:
            await move_message.answer('Твой ход принят. Ожидай своего соперника.')

    @classmethod
    def register_moves_handlers(cls, router: Router):
        router.message.register(cls.handle_game_move_message, F.dice)

