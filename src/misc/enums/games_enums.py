from enum import IntEnum, Enum
from typing import Final


class EvenUnevenBetOption(Enum):
    LESS_7 = 'A'
    EQUALS_7 = 'B'
    GREATER_7 = 'C'
    EVEN = 'D'
    UNEVEN = 'E'
    A_EQUALS_B = 'F'

    def get_coefficient(self) -> float:
        match self:
            case self.LESS_7: return 1.4
            case self.EQUALS_7: return 3
            case self.GREATER_7: return 1.4
            case self.EVEN: return 1.5
            case self.UNEVEN: return 1.5
            case self.A_EQUALS_B: return 3


class BaccaratBettingOption(IntEnum):
    NOT_MOVED = 0
    PLAYER = 1
    TIE = 2
    BANKER = 3


class GameCategory(str, Enum):
    BASIC = 'Игры'
    BLACKJACK = 'BlackJack'
    BACCARAT = 'Baccarat'
    EVEN_UNEVEN = 'EuN'


class GameType(str, Enum):
    """Эмодзи с типом игры"""
    DICE = '🎲'
    CASINO = '🎰'
    DARTS = '🎯'
    BOWLING = '🎳'
    BASKETBALL = '🏀'
    FOOTBALL = '⚽'
    BJ = '♠'
    BACCARAT = '🎴'

    def get_full_name(self) -> str:
        """Возвращает строку с полным именем игры"""
        match self:
            case GameType.DICE: return "Кости"
            case GameType.CASINO: return "Слоты"
            case GameType.DARTS: return "Дартс"
            case GameType.BOWLING: return "Боулинг"
            case GameType.BASKETBALL: return "Баскетбол"
            case GameType.FOOTBALL: return "Футбол"
            case GameType.BJ: return 'BlackJack'
            case GameType.BACCARAT: return 'Баккарат'
            case _: return "Игра"


class GameStatus(IntEnum):
    CANCELED = -1
    WAIT_FOR_PLAYERS = 0
    ACTIVE = 1
    FINISHED = 2
