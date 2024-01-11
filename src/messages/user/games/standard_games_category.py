from src.messages.user.games.game_messages_abc import GameCategoryMessages


class StandardGameCategoryMessages(GameCategoryMessages):
    @staticmethod
    def get_category_photo() -> str:
        return 'https://telegra.ph/file/b2d6791839dffc50bae8b.png'

    @staticmethod
    def get_category_description(player_name: str) -> str:
        return (
            "<b>🎲 Games — 6 игровых режимов:</b> Кости, Дартс, Баскетбол, Слоты, Боулинг, Футбол \n\n"
            "Твоя задача в них: набрать больше очков, чем твой соперник и победа будет за тобой. \n"
            "Переходи к игровым столам, нажав кнопку «➕ Создать»"
        )
