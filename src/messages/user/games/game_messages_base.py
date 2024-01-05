from abc import ABC, abstractmethod


class BotGamesMessagesBase(ABC):

    @staticmethod
    @abstractmethod
    def get_game_started():
        pass

    @staticmethod
    @abstractmethod
    def get_tie():
        pass

    @staticmethod
    @abstractmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        pass

    @staticmethod
    @abstractmethod
    def get_player_loose():
        pass
