from src.messages.user.games.game_messages_abc import BotGamesMessagesBase, CreatableGamesMessages


class SlotsMessages(BotGamesMessagesBase, CreatableGamesMessages):

    @staticmethod
    def get_ask_for_bet_photo() -> str:
        return 'https://telegra.ph/file/366a2258c2891e638d698.png'
