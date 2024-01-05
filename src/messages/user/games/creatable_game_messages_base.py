from abc import ABC, abstractmethod


class CreatableGamesMessages(ABC):
    @staticmethod
    @abstractmethod
    def get_category_description(player_name: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def ask_for_bet_amount(player_name: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_game_created(game_number: int):
        pass
