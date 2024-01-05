import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message

from src.database import games, Game, transactions, PlayerScore, User
from src.database.games import game_scores
from src.handlers.user.bot.game_strategies.game_strategy import GameStrategy
from src.keyboards import UserMenuKeyboards, UserPrivateGameKeyboards
from src.messages import UserPublicGameMessages
from src.misc import GameStatus
from src.utils.choose_game_messages import get_message_instance_by_game_type
from src.utils.game_messages_sender import GameMessageSender
from src.utils.timer import BaseTimer


class GameTimer(BaseTimer):

    async def make_tick(self):
        pass

    async def on_time_left(self):
        pass


class BasicGameStrategy(GameStrategy):

    @staticmethod
    async def start_game(bot: Bot, game: Game):
        msg_instance = get_message_instance_by_game_type(game_type=game.game_type)
        text = msg_instance.get_game_started()
        markup = UserPrivateGameKeyboards.get_dice_kb(game.game_type.value)
        await GameMessageSender(bot, game).send(text, markup=markup)

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
        if game and dice.emoji == game.game_type.value:
            await cls.process_player_move(game, message)

        # если все походили заканчиваем игру
        if len(await game_scores.get_game_moves(game)) == game.max_players:
            await cls.finish_game(bot=message.bot, game=game)

    @classmethod
    async def process_player_move(cls, game: Game, message: Message):
        """Обрабатывает ход в игре"""
        game_moves = await game_scores.get_game_moves(game)
        player_telegram_id = message.from_user.id
        dice_value = message.dice.value

        # если не все игроки сделали ходы
        if len(game_moves) != game.max_players:
            await game_scores.add_player_move_if_not_moved(
                game=game, player_telegram_id=player_telegram_id, move_value=dice_value
            )

    @classmethod
    def register_moves_handlers(cls, router: Router):
        router.message.register(cls.handle_game_move_message, F.dice)
