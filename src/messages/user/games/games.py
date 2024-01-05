from typing import List

from aiogram import html

from src.database import games, users, Game, PlayerScore, get_top_winners_by_amount, User
from src.messages.user.games.creatable_game_messages_base import CreatableGamesMessages
from src.messages.user.games.game_messages_base import BotGamesMessagesBase
from src.utils.text_utils import format_float_to_rub_string
from src.misc import GameCategory
from settings import Config


# region Utils

async def get_short_game_info_text(game: Game) -> str:
    """Возвращает строку с коротким описанием игры"""
    header = get_game_header(game)
    creator = await games.get_creator_of_game(game)

    return f'{header} \n' \
           f'👤 Создал: {str(creator)} \n' \
           f'💰 Ставка: {format_float_to_rub_string(game.bet, use_html=False)} \n'


async def get_full_game_info_text(game: Game):
    header = html.bold(get_game_header(game))
    players_text = f"👥 Игроки: \n{await _get_game_participants(game)}"
    bet_text = f"💰 Ставка: {format_float_to_rub_string(game.bet, use_html=False)}"
    return f'{header} \n\n{players_text} \n\n{bet_text}'


def get_game_header(game: Game):
    return f'{game.game_type.value} {game.game_type.get_full_name()} №{game.number}'


async def _get_players_results(game_moves: list[PlayerScore]) -> str:
    strings = []

    for move in game_moves:
        strings.append(f"{str(await move.player.get())} - [{move.value}]")

    return '\n'.join(strings)


async def _get_game_participants(game: Game):
    number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
    players = await games.get_players_of_game(game)
    # заполняем недостающие места None
    players = [*players, *(None,) * (game.max_players - len(players))]
    player_strings = []

    for emoji, player in zip(number_emojis, players):
        text = str(player) if player else 'Ожидание...'
        player_strings.append(f"{emoji} - {text}")

    return '\n'.join(player_strings)


# endregion Utils


class UserPrivateGameMessages(CreatableGamesMessages):
    """Содержит функции для получения текстов сообщений, связанных с играми и отправляемых в боте"""

    @staticmethod
    def get_category_description(player_name: str) -> str:
        return "🎲 Классические игры"

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        pass

    @staticmethod
    def get_game_category(category: GameCategory) -> str:
        return f'{category.value} \n'

    @staticmethod
    async def get_game_category_stats(category: GameCategory) -> str:
        time_periods = [
            {'label': '👤 За сутки:', 'days_back': 1},
            {'label': '\n👤 За месяц:', 'days_back': 30},
            {'label': '\n👤 За всё время:', 'days_back': None}
        ]

        text = f"{html.bold('📊 Статистика')} \n\n"
        medals = ('🥇', '🥈', '🥉')
        for period in time_periods:
            top_winnings = await get_top_winners_by_amount(category, days_back=period['days_back'], limit=3)
            text += f"{html.bold(period['label'])} \n"
            for medal, user in zip(medals, top_winnings):
                text += f"{medal} {user} [{format_float_to_rub_string(user.winnings_amount)}]\n"

        text += html.bold("\nℹ В статистику входят суммы ставок")
        return text

    @staticmethod
    def get_choose_game_type() -> str:
        return '🧩 Выберите тип игры:'

    @staticmethod
    async def enter_bet_amount(
            user_id: int, game_type_name: str, message_instance: CreatableGamesMessages = None
    ) -> str:
        """Просьба ввести ставку"""
        user = await users.get_user_or_none(user_id)

        # Уникальный для игрового режима текст
        game_type_unique_text = f"{message_instance.ask_for_bet_amount(user.name)}\n\n" if message_instance else ""

        return f'➕ Создание игры в {game_type_name} \n\n' \
               f'{game_type_unique_text}'\
               f'— Минимальная сумма ставки: {format_float_to_rub_string(Config.Games.min_bet_amount)} \n' \
               f'— Ваш баланс: {format_float_to_rub_string(user.balance)} \n\n' \
               f'ℹ Введите размер ставки или нажмите Отмена'

    @staticmethod
    def get_game_created(game: Game) -> str:
        game_type = game.game_type
        return f'✅ Игра {game_type.value} {game_type.get_full_name()} №{game.number} создана. \n\n' \
               f'⏰ Скоро кто-то присоединится...'

    @staticmethod
    def get_game_successfully_canceled():
        return 'Игра отменена'

    @staticmethod
    def get_its_last_page():
        return 'Это последняя страница.'


class UserPublicGameMessages(BotGamesMessagesBase):
    """Содержит функции для получения текстов сообщений, связанных с играми и отправляемых в чаты"""

    @staticmethod
    def get_game_started() -> str:
        return 'Нажмите на клавиатуру, чтобы походить'

    @staticmethod
    def get_tie():
        return

    @staticmethod
    def get_player_loose():
        return

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        return

    @staticmethod
    async def get_game_created_in_bot_notification(game: Game, bot_username: str) -> str:
        bot_url = f'https://t.me/{bot_username}'

        return html.bold(
            f'{html.link("🌐 Создана новая игра в боте", link=bot_url)} \n\n'
            f'{await get_full_game_info_text(game)}'
        )

    @staticmethod
    async def get_game_in_chat_created(game: Game, chat_username: str = None):
        chat_header = html.link('🌐 Создана новая игра в чате', f'https://t.me/{chat_username}/')
        base = await get_short_game_info_text(game)
        places = f"🚪 Свободных мест: {len(await games.get_player_ids_of_game(game))}/{game.max_players} чел."

        return html.bold(f"{chat_header} \n\n{base} \n{places}")

    @staticmethod
    async def get_game_in_chat_start(game: Game) -> str:
        base = await get_full_game_info_text(game)
        ask_dice_text = f"— Отправьте  {html.code(f'{game.game_type.value}')}  в ответ на это сообщение:"

        result = f"{base} \n\n{ask_dice_text}"
        return result

    @staticmethod
    async def get_game_in_chat_finish(
            game: Game, game_moves: list[PlayerScore], winners: List[User], win_amount: float | None
    ):
        # Получаем заголовок игры
        header = get_game_header(game)

        # Получаем результаты игры
        results = f"📊 Результаты: \n{await _get_players_results(game_moves)}"

        # Формируем сообщение о победителе и выигрыше
        if not winners:
            winner_text = '⚡⚡⚡ Ничья ⚡⚡⚡ \n♻ Возвращаю ставки'
        elif len(winners) > 1:
            winner_text = (
                f'💰 Выигрыш: {format_float_to_rub_string(win_amount)}\n'
                f'🏆 Победители: {", ".join(str(winner) for winner in winners)} \n'
            )
        else:
            winner_text = (
                f'💰 Выигрыш: {format_float_to_rub_string(win_amount)}\n'
                f'🏆 Победитель: {winners[0]} \n'
            )
        # Собираем сообщение
        return f"{header}\n\n{results}\n\n{winner_text}"

    # region MiniGames
    @staticmethod
    def get_mini_game_victory(game: Game, win_amount: float):
        return f'👤 {str(game.creator)} \n' \
               f'🎉 Вы выиграли! \n' \
               f'➕ Сумма выигрыша: {format_float_to_rub_string(win_amount)}'

    @staticmethod
    def get_mini_game_loose(game: Game) -> str:
        return f'👤 {str(game.creator)} \n' \
               f'😞 Вы проиграли {format_float_to_rub_string(game.bet)} \n' \
               f'🍀 Возможно, в следующий раз повезёт'
