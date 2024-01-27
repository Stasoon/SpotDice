from aiogram import Router

from src.filters import ChatTypeFilter, ActiveGameFilter
from src.middlewares import ThrottlingMiddleware
from src.handlers.user.bot.game_strategies.mines import register_mines_handlers
from .even_uneven import register_even_uneven_handlers
from .start_command import register_start_command_handler
from .menu_options import register_menu_options_handlers
from src.handlers.user.bot.join_and_confirm_game import register_join_game_handlers
from .game_strategies import register_games_strategies_handlers


def register_bot_handlers(router: Router):
    # Фильтр, что апдейты в приватном чате
    router.message.filter(ChatTypeFilter('private'))
    router.callback_query.filter(ChatTypeFilter('private'))

    # Регистрация throttling middleware на сообщения и калбэки
    router.message.middleware(ThrottlingMiddleware())
    router.callback_query.middleware(ThrottlingMiddleware())

    confirm_router = Router(name='confirm_game_router')
    # Регистрация присоединения к игре
    register_join_game_handlers(confirm_router)

    # Регистрация команды /start
    menu_router = Router(name='bot_menu_router')
    menu_router.message.filter(ActiveGameFilter(user_should_have_active_game=False))
    menu_router.callback_query.filter(ActiveGameFilter(user_should_have_active_game=False))
    register_start_command_handler(menu_router)

    # Регистрация опций меню
    register_menu_options_handlers(menu_router)

    # Регистрация ввода ставки even_uneven
    register_even_uneven_handlers(menu_router)

    # Регистрация игрового процесса
    games_router = Router(name='games_router')
    register_games_strategies_handlers(games_router)

    router.include_routers(confirm_router, menu_router, games_router)
