from aiogram import Dispatcher, Router

from src.filters import ChatTypeFilter, UserExistFilter
from .commands import register_commands_handlers
from src.handlers.user.chat.games_process.game_actions import register_game_actions_handlers


def register_chat_handlers(router: Dispatcher | Router):
    router.message.filter(ChatTypeFilter(chat_type=['group', 'supergroup']), UserExistFilter(True))
    router.callback_query.filter(ChatTypeFilter(chat_type=['group', 'supergroup']), UserExistFilter(True))

    register_commands_handlers(router)
    register_game_actions_handlers(router)
