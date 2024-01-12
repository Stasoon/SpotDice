from typing import Type, Union

from src.messages.user.games.slots import SlotsMessages
from src.misc import GameType, GameCategory
from src.messages.user.games import BlackJackMessages, BaccaratMessages, BasketballMessages
from src.messages.user.games.bowling import BowlingMessages
from src.messages.user.games.darts import DartsMessages
from src.messages.user.games.dice import DiceMessages
from src.messages.user.games.football import FootballMessages
from src.messages.user.games.standard_games_category import StandardGameCategoryMessages
from src.messages.user.games.game_messages_abc import CreatableGamesMessages, GameCategoryMessages, BotGamesMessagesBase


def get_game_category_message_instance(game_category: GameCategory) -> Type[GameCategoryMessages]:
    match game_category:
        case GameCategory.BLACKJACK:
            return BlackJackMessages
        case GameCategory.BACCARAT:
            return BaccaratMessages
        case GameCategory.BASIC:
            return StandardGameCategoryMessages


def get_message_instance_by_game_type(game_type: GameType) -> Type[Union[CreatableGamesMessages, BotGamesMessagesBase]]:
    match game_type:
        case GameType.BJ:
            return BlackJackMessages
        case GameType.BACCARAT:
            return BaccaratMessages
        case GameType.BASKETBALL:
            return BasketballMessages
        case GameType.FOOTBALL:
            return FootballMessages
        case GameType.BOWLING:
            return BowlingMessages
        case GameType.DARTS:
            return DartsMessages
        case GameType.DICE:
            return DiceMessages
        case GameType.CASINO:
            return SlotsMessages
