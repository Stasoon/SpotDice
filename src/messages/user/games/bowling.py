from src.messages.user.games.creatable_game_messages_base import CreatableGamesMessages
from src.messages.user.games.game_messages_base import BotGamesMessagesBase


class BowlingMessages(BotGamesMessagesBase, CreatableGamesMessages):

    @staticmethod
    def get_category_description(player_name: str) -> str:
         pass

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        pass

    @staticmethod
    def get_game_created(game_number: int):
        pass

    @staticmethod
    def get_game_started():
        pass

    @staticmethod
    def get_tie():
        pass

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        pass

    @staticmethod
    def get_player_loose():
        pass