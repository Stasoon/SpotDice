from aiogram import Router

from .mini_games import register_mini_games_handlers
from .base_games import register_games_for_two_commands_handlers
from .card_games import register_card_games_handlers
from .other_commands import register_other_commands_handlers


def register_commands_handlers(router: Router):
    register_mini_games_handlers(router)
    register_games_for_two_commands_handlers(router)
    register_other_commands_handlers(router)
    register_card_games_handlers(router)
