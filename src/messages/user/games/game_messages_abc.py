from abc import ABC, abstractmethod


class GameCategoryMessages(ABC):
    @staticmethod
    @abstractmethod
    def get_category_description(player_name: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_category_photo() -> str:
        pass


class CreatableGamesMessages(ABC):
    @staticmethod
    @abstractmethod
    def ask_for_bet_amount(player_name: str) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_game_created(game_number: int):
        return f'✅ Игра №{game_number} создана. \n\n⏰ Скоро кто-то присоединится...'


class BotGamesMessagesBase(ABC):
    @staticmethod
    @abstractmethod
    def get_game_started() -> str:
        return 'Игра началась!'

    @staticmethod
    @abstractmethod
    def get_tie() -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_player_loose() -> str:
        pass
