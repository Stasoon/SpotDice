import asyncio
from typing import Collection, Union, Any, Generator

from aiogram import Router, F, Bot
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove

from src.database import Game, PlayerScore, games, transactions
from src.database.games import playing_cards, game_scores
from src.handlers.user.bot.game_strategies.game_strategy import GameStrategy
from src.misc.enums import BaccaratBettingOption
from src.utils.game_messages_sender import GameMessageSender
from src.utils.card_images import BaccaratImagePainter
from src.keyboards.user.games import BaccaratKeyboards
from src.messages.user.games import BaccaratMessages
from src.keyboards import UserMenuKeyboards
from src.misc import GameStatus
from src.utils.cards import get_shuffled_deck, Card
from settings import Config
from src.utils.timer import BaseTimer

# region Utils

BANKER_ID = 0
PLAYER_ID = 1


def get_points_of_card(card: Card) -> int:
    """ Возвращает количество очков, которое даёт конкретная карта """
    if card.value in ["10", "В", "Д", "К"]:
        return 0
    elif card.value == 'Т':
        return 1
    else:
        return int(card.value)


def count_player_points(cards: list[Card]) -> int:
    """ Рассчитывает  """
    points = (get_points_of_card(card) for card in cards)
    return sum(points) % 10


async def deal_card(deck: Generator[Card, Any, Any], player_id: int, game: Game):
    """
    Получает следующую карту из колоды и сохраняет её в базу данных.
    Возвращает полученную карту.
    """
    card = next(deck)
    await playing_cards.add_card_to_player_hand(
        game_number=game.number, player_telegram_id=player_id,
        card_suit=card.suit, card_value=card.value,
        points=get_points_of_card(card)
    )
    return card


def get_win_coefficient(winner: BaccaratBettingOption):
    """ Возвращает коэффициент, который получат игроки, поставившие на выигравшую опцию"""
    match winner:
        case BaccaratBettingOption.PLAYER:
            return 2
        case BaccaratBettingOption.BANKER:
            return 1.95
        case BaccaratBettingOption.TIE:
            return 8


def check_clear_win_and_get_won_option(player_points: int, banker_points: int) -> Union[BaccaratBettingOption, None]:
    """
    Проверяет, есть ли чистая победа у игрока или банкира.
    Если есть - возвращает победившую опцию, иначе - None
    """
    if player_points not in (8, 9) and banker_points not in (8, 9):
        return None

    if (player_points == 9 and banker_points < 9) or (player_points == 8 and banker_points < player_points):
        return BaccaratBettingOption.PLAYER
    elif (player_points != 9 and banker_points == 9) or (banker_points == 8 and player_points < banker_points):
        return BaccaratBettingOption.BANKER
    return None


def should_dealer_pick_third_card(banker_points: int, player_third_card: Card) -> bool:
    """
    По специальной таблице проверяет, должен ли брать дилер третью карту.
    Решение зависит от текущих очков банкира и того, какая третья карта у игрока.
    """
    card_points = get_points_of_card(player_third_card)
    flag = (
            (0 <= banker_points <= 2) or
            (banker_points == 3 and (card_points <= 7 or card_points == 9)) or
            (banker_points == 4 and 2 <= card_points <= 7) or
            (banker_points == 5 and 4 <= card_points <= 7) or
            (banker_points == 6 and 6 <= card_points <= 7)
    )
    return True if flag else False


def get_winner(banker_points: int, player_points: int) -> BaccaratBettingOption:
    """ Получает победившую опцию (ничья/банкир/игрок) на основе очков банкира и игрока. """
    if banker_points == player_points:
        return BaccaratBettingOption.TIE
    elif player_points > banker_points:
        return BaccaratBettingOption.PLAYER
    else:
        return BaccaratBettingOption.BANKER


async def process_game_and_get_won_option(bot: Bot, game: Game):
    deck = get_shuffled_deck(decks_count=3)

    player_cards = [await deal_card(player_id=PLAYER_ID, game=game, deck=deck) for _ in range(2)]
    banker_cards = [await deal_card(player_id=BANKER_ID, game=game, deck=deck) for _ in range(2)]

    player_points = count_player_points(player_cards)
    banker_points = count_player_points(banker_cards)

    # Если набрано 8 или 9 очков первыми двумя картами
    winner = check_clear_win_and_get_won_option(player_points, banker_points)
    if winner:
        return winner

    # выдача карты игроку, если от 0 до 5 очков
    sender = GameMessageSender(bot, game)
    if player_points <= 5:
        player_third_card = await deal_card(deck=deck, player_id=PLAYER_ID, game=game)
        await sender.send(text='Игрок берёт третью карту...')
        await asyncio.sleep(1)

        # если игрок взял третью карту, проверяем, должен ли банкир брать карту по правилам
        if should_dealer_pick_third_card(banker_points, player_third_card):
            await deal_card(deck=deck, player_id=BANKER_ID, game=game)
            await sender.send(text='Дилер берёт третью карту...')
            await asyncio.sleep(1)
    # если игрок не взял карту, но у дилера от 0 до 5, берёт карту
    elif banker_points < 6:
        await deal_card(deck=deck, player_id=BANKER_ID, game=game)
        await sender.send(text='Дилер берёт третью карту...')
        await asyncio.sleep(1)


async def send_result_to_players(bot, game: Game, bet_choices: Collection[PlayerScore]):
    """ Отправляет результаты игры всем её участникам, а также в игровой чат. """
    player_ids = await games.get_player_ids_of_game(game)

    # отправляем action загрузки фото
    try:
        await asyncio.gather(*[
            bot.send_chat_action(chat_id=player_id, action=ChatAction.UPLOAD_PHOTO)
            for player_id in player_ids
        ])
    except TelegramNetworkError:
        pass

    # Генерируем фото и загружаем из буфера. Отправляем первому юзеру

    image_painter = BaccaratImagePainter(game=game)
    img = await image_painter.get_image()

    result_photo_file_id = (await bot.send_photo(
        chat_id=player_ids[0], photo=img
    )).photo[0].file_id

    # Копируем фото другим игрокам, если оно создалось успешно
    sender = GameMessageSender(bot, game)
    if result_photo_file_id:
        await sender.send(photo=result_photo_file_id, player_ids=player_ids[1:])

    # Отправляем сообщение с результатами игры всем игрокам
    text = await BaccaratMessages.get_baccarat_results(bet_choices)
    reply_markup = UserMenuKeyboards.get_main_menu()
    await sender.send(text, markup=reply_markup)

    # отправляем сообщение о том, что игра завершена, в чат
    await bot.send_photo(
        photo=result_photo_file_id,
        chat_id=game.chat_id if game.chat_id < 0 else Config.Games.GAME_CHAT_ID,
        caption=text,
        parse_mode='HTML'
    )


class BaccaratTimer(BaseTimer):

    def __init__(self, bot: Bot, game: Game, chat_id: int, message_id: int, seconds_expiry: int, text_template: str):
        super().__init__(chat_id, message_id, seconds_expiry)

        self.bot = bot
        self.game = game
        self.template = text_template

    @classmethod
    async def stop(cls, bot: Bot, chat_id: int):
        try:
            timer = await super(BaccaratTimer, cls).stop(chat_id)
            await bot.delete_message(chat_id=timer.chat_id, message_id=timer.message_id)
        except Exception:
            pass

    async def make_tick(self):
        await super(BaccaratTimer, self).make_tick()

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
            return
        else:
            await self.bot.send_message(chat_id=self.timer.chat_id, text="Время на ход вышло!")
            await game_scores.add_player_move_if_not_moved(
                self.game, self.timer.chat_id, move_value=BaccaratBettingOption.NOT_MOVED.value
            )

            if await game_scores.is_all_players_moved(self.game):
                await BaccaratStrategy.finish_game(self.bot, self.game)

        await self.timer.delete()


# endregion Utils

# region Handlers


class BaccaratStrategy(GameStrategy):

    @staticmethod
    async def start_game(bot: Bot, game: Game):
        """Когда все игроки собраны, вызывается функция для старта игры в баккара"""
        time_on_move = 5*60
        player_ids = await games.get_player_ids_of_game(game)

        text = BaccaratMessages.get_bet_prompt()
        counter_text = "⏱ Время на ход: {0}"
        reply_markup = BaccaratKeyboards.get_bet_options()

        timers = []

        for player_id in player_ids:
            await bot.send_message(chat_id=player_id, text=text, reply_markup=reply_markup)
            counter_msg = await bot.send_message(
                chat_id=player_id, text=counter_text.format(BaccaratTimer.format_seconds_to_time(time_on_move))
            )

            timer = BaccaratTimer(
                bot=bot, game=game,
                chat_id=player_id, message_id=counter_msg.message_id,
                seconds_expiry=time_on_move, text_template=counter_text,
            )

            # Создаем задачу для таймера и добавляем ее в список
            timers.append(asyncio.create_task(timer.start()))

        await asyncio.gather(*timers)

    @staticmethod
    def __interpret_user_bet_choice(bet_text: str) -> int:
        """ Возвращает тип """
        match bet_text:
            case '👤 Игрок':
                return BaccaratBettingOption.PLAYER.value
            case '🤝 Ничья':
                return BaccaratBettingOption.TIE.value
            case '🏦 Банкир':
                return BaccaratBettingOption.BANKER.value

    @classmethod
    async def handle_bet_move_message(cls, message: Message) -> None:
        """Обрабатывает сообщение с тем, на кого ставит игрок - банк, ничью, игрока"""
        await BaccaratTimer.stop(bot=message.bot, chat_id=message.from_user.id)

        user_id = message.from_user.id
        game = await games.get_user_unfinished_game(user_id)
        if not game:
            return

        betting_option_number = cls.__interpret_user_bet_choice(message.text)
        if not betting_option_number:
            return

        # Сохраняем ставку
        await game_scores.add_player_move_if_not_moved(game, user_id, betting_option_number)
        await message.answer(text='Ваша ставка принята', reply_markup=ReplyKeyboardRemove())

        if await game_scores.is_all_players_moved(game):
            await BaccaratStrategy.finish_game(message.bot, game)

    @staticmethod
    async def finish_game(bot: Bot, game: Game):
        if game.status != GameStatus.ACTIVE:
            return
        await games.finish_game(game)

        await GameMessageSender(bot, game).send(text='Все игроки сделали ставки')
        await process_game_and_get_won_option(game=game, bot=bot)

        player_res = await playing_cards.count_player_score(game_number=game.number, player_id=PLAYER_ID) % 10
        banker_res = await playing_cards.count_player_score(game_number=game.number, player_id=BANKER_ID) % 10
        won_option = get_winner(banker_points=banker_res, player_points=player_res)

        win_coefficient = get_win_coefficient(won_option)
        bet_choices = await game_scores.get_game_moves(game)

        for choice in bet_choices:
            if choice.value == won_option.value:
                await transactions.accrue_winnings(
                    game_category=game.category,
                    winner_telegram_id=(await choice.player.get()).telegram_id,
                    amount=game.bet * win_coefficient
                )

        await send_result_to_players(bot, game, bet_choices)
        await game_scores.delete_game_scores(game)
        await playing_cards.delete_game_cards(game_number=game.number)

    @classmethod
    def register_moves_handlers(cls, router: Router):
        router.message.register(BaccaratStrategy.handle_bet_move_message, F.text)
