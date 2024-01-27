from src.messages.user.games.game_messages_abc import GameCategoryMessages


class MinesMessages(GameCategoryMessages):

    @staticmethod
    def get_category_description(player_name: str) -> str:
        return '💎 Mines - ищите алмазы, умножайте свою ставку, но остерегайтесь мин!'

    @staticmethod
    def get_category_photo() -> str:
        return 'https://telegra.ph/file/224fb77851f4d6edcc47a.png'

    @staticmethod
    def get_setup_game() -> str:
        return 'Выберите ставку и количество мин:'
