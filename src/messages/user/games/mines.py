from src.messages.user.games.game_messages_abc import GameCategoryMessages
from src.utils.text_utils import format_float_to_rub_string


class MinesMessages(GameCategoryMessages):

    @staticmethod
    def get_category_description(player_name: str) -> str:
        return '<b>💎 Mines</b> - ищите алмазы, умножайте свою ставку, но остерегайтесь мин!'

    @staticmethod
    def get_category_photo() -> str:
        return 'https://telegra.ph/file/224fb77851f4d6edcc47a.png'

    @staticmethod
    def get_setup_game(balance: float) -> str:
        return (
            f'💰 Баланс: {format_float_to_rub_string(balance)} \n\n'
            f'💎 Выберите ставку и количество мин:'
        )

    @staticmethod
    def get_game_started():
        return '🔎  <code>Угадай, где нет мины:</code>'

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0) -> str:
        return f'🎉  Ты выиграл {format_float_to_rub_string(win_amount)}!'

    @staticmethod
    def get_player_loose() -> str:
        return '💥 <b>Ты нарвался на мину!</b>'
