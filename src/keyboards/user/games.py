from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums.dice_emoji import DiceEmoji

from src.database import Game, games
from src.misc import GameType, GameCategory, GameStatus
from src.misc.callback_factories import (
    BlackJackCallback, GamesCallback, MenuNavigationCallback, GamePagesNavigationCallback
)
from src.misc.enums.games_enums import EvenUnevenBetOption


class BaccaratKeyboards:
    @staticmethod
    def get_bet_options() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='👤 Игрок')],
            [KeyboardButton(text='🤝 Ничья')],
            [KeyboardButton(text='🏦 Банкир')],
        ])


class EvenUnevenKeyboards:
    @staticmethod
    def get_cancel_bet_entering() -> InlineKeyboardMarkup:
        cancel_button = InlineKeyboardButton(text='Отменить', callback_data='cancel_even_uneven_bet')
        return InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])

    @staticmethod
    def get_bet_options(round_number: int, bot_username: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        url = f'https://t.me/{bot_username}?start=EuN_{round_number}_' + '{move}'
        builder.button(text='< 7', url=url.format(move=EvenUnevenBetOption.LESS_7.value))
        builder.button(text='= 7', url=url.format(move=EvenUnevenBetOption.EQUALS_7.value))
        builder.button(text='> 7', url=url.format(move=EvenUnevenBetOption.GREATER_7.value))
        builder.button(text='Чёт', url=url.format(move=EvenUnevenBetOption.EVEN.value))
        builder.button(text='Нечёт', url=url.format(move=EvenUnevenBetOption.UNEVEN.value))
        builder.button(text='D1 = D2', url=url.format(move=EvenUnevenBetOption.A_EQUALS_B.value))
        builder.adjust(3, 2, 1)
        return builder.as_markup()


class BlackJackKeyboards:
    @staticmethod
    def get_controls(game_number: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='👇 Взять', callback_data=BlackJackCallback(game_number=game_number, move='take'))
        builder.button(text='✋ Хватит', callback_data=BlackJackCallback(game_number=game_number, move='stand'))
        return builder.as_markup()
        # "🙅‍♂ Отказаться"


# клавиатуры для отображения в боте
class UserPrivateGameKeyboards:
    @staticmethod
    def get_dice_kb(dice_emoji: str) -> ReplyKeyboardMarkup:
        """Возвращает reply клавиатуру с эмодзи"""
        dice_button = KeyboardButton(text=dice_emoji)
        return ReplyKeyboardMarkup(
            keyboard=[[dice_button]], one_time_keyboard=True,
            input_field_placeholder='Нажмите, чтобы походить ⬇'
        )

    @staticmethod
    def get_play_menu() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, которая должна отображаться после перехода в Играть"""
        builder = InlineKeyboardBuilder()

        builder.button(text='🎲 Games', callback_data=GamesCallback(action='show', game_category=GameCategory.BASIC))
        builder.button(text='♠ BlackJack', callback_data=GamesCallback(
            action='show', game_category=GameCategory.BLACKJACK, game_type=GameType.BJ))
        builder.button(text='🎴 Baccarat', callback_data=GamesCallback(
            action='show', game_category=GameCategory.BACCARAT, game_type=GameType.BACCARAT))
        builder.button(text='EvenUneven', url='https://t.me/SpotDiceU')
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def get_game_category(
            available_games: list[Game], category: GameCategory, current_page_num: int
    ) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, которая должна отображаться при нажатии на категорию игр"""
        builder = InlineKeyboardBuilder()
        builder.button(text='➕ Создать', callback_data=GamesCallback(action='create', game_category=category))
        builder.button(text='♻ Обновить', callback_data=GamesCallback(action='refresh', game_category=category))
        builder.adjust(2)
        builder.button(text='📊 Статистика', callback_data=GamesCallback(action='stats', game_category=category))

        # Добавление игр
        for game in available_games:
            text = f'{game.game_type.value}#{game.number} | 💰{game.bet} | {(await game.creator.first()).name}'
            builder.button(
                text=text,
                callback_data=GamesCallback(action='show', game_category=category, game_number=game.number)
            ).row()

        # Навигация по страницам с играми
        navigation_builder = InlineKeyboardBuilder()
        navigation_builder.button(text='◀', callback_data=GamePagesNavigationCallback(
            direction='prev', category=category, current_page=current_page_num))
        navigation_builder.button(text='▶', callback_data=GamePagesNavigationCallback(
            direction='next', category=category, current_page=current_page_num))
        navigation_builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='game_strategies'))
        navigation_builder.adjust(2, 1)

        builder.adjust(2, 1).attach(navigation_builder)
        return builder.as_markup()

    @staticmethod
    def get_back_from_stats(category: GameCategory) -> InlineKeyboardMarkup:
        """Возвращает кнопку для возврата из окна со статистикой по категории игр"""
        builder = InlineKeyboardBuilder()
        builder.button(text='🔙 Назад', callback_data=GamesCallback(action='show', game_category=category))
        return builder.as_markup()

    @staticmethod
    def get_basic_game_types() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для выбора типа базовой игры при её создании"""
        builder = InlineKeyboardBuilder()
        # ide может ругаться, но всё в порядке
        dice_emojis = [emoji.value for emoji in DiceEmoji]

        for game_type in GameType:
            if game_type.value in dice_emojis:
                builder.button(
                    text=f'{game_type.value} {game_type.get_full_name()}',
                    callback_data=GamesCallback(
                        action='create',
                        game_category=GameCategory.BASIC,
                        game_type=game_type
                    )
                )

        builder.adjust(2)
        back_builder = InlineKeyboardBuilder()
        back_builder.button(text='🔙 Назад',
                            callback_data=GamesCallback(action='show', game_category=GameCategory.BASIC))
        builder.attach(back_builder)
        return builder.as_markup()

    @staticmethod
    def get_cancel_bet_entering(game_category: GameCategory) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='🔙 Отмена', callback_data=GamesCallback(action='show', game_category=game_category))
        return builder.as_markup()

    @staticmethod
    async def get_join_game_or_back(user_id: int, game: Game) -> InlineKeyboardMarkup:
        """Клавиатура для просмотра игры из меню"""
        game_creator = await games.get_creator_of_game(game)
        builder = InlineKeyboardBuilder()

        if game_creator.telegram_id != user_id:
            builder.button(
                text='⚡ Принять ставку ⚡',
                callback_data=GamesCallback(action='join', game_category=game.category, game_number=game.number)
            )

        # Если пользователь - создатель игры, и она ещё не началась, добавляем кнопку отмены игры
        if game_creator.telegram_id == user_id and game.status == GameStatus.WAIT_FOR_PLAYERS:
            builder.button(text='❌ Отменить ❌', callback_data=GamesCallback(
                game_number=game.number, action='cancel', game_category=game.category
            ))

        builder.button(text='🔙 Назад', callback_data=GamesCallback(action='show', game_category=game.category))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def show_game(game: Game) -> InlineKeyboardMarkup | None:
        """Принять ставку (когда перешёл в бота)"""
        if len(await games.get_players_of_game(game)) == game.max_players:
            return None

        builder = InlineKeyboardBuilder()

        builder.button(
            text=f'{game.game_type.value} Присоединиться',
            callback_data=GamesCallback(
                action='join', game_number=game.number,
                game_category=game.category, game_type=game.game_type
            )
        )

        return builder.as_markup()


# клавиатуры для отображения в чатах
class UserPublicGameKeyboards:
    @staticmethod
    async def get_go_to_bot_and_join(game: Game, bot_username: str):
        """Перейти в бота с кнопкой старт и показать игру (кнопка для чата)"""
        if len(await games.get_players_of_game(game)) == game.max_players:
            return None

        builder = InlineKeyboardBuilder()
        builder.button(
            text='🔗 Присоединиться в боте',
            url=f"https://t.me/{bot_username}?start=_{game.game_type.name}_{game.number}"
        )
        return builder.as_markup()

    @staticmethod
    async def get_join_game_in_chat(game: Game) -> InlineKeyboardMarkup | None:
        """Клавиатура под игрой для чата"""
        if len(await games.get_players_of_game(game)) == game.max_players:
            return None

        builder = InlineKeyboardBuilder()
        builder.button(
            text='✅ Присоединиться', callback_data=GamesCallback(action='join', game_number=game.number)
        )
        return builder.as_markup()
