from aiogram import Router

from .basic_games import BasicGameStrategy
from .baccarat import BaccaratStrategy
from .blackjack import BlackJackStrategy
from .mines import register_mines_handlers


def register_games_strategies_handlers(router: Router):
    game_strategies = (
        BaccaratStrategy,
        BlackJackStrategy,
        BasicGameStrategy
    )

    for strategy in game_strategies:
        strategy.register_moves_handlers(router)
    register_mines_handlers(router)
