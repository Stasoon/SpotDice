from aiogram import Router

from .bot import register_bot_handlers
from .chat import register_chat_handlers
from .other import register_other_handlers
from ...middlewares.user_activity import UserActivityMiddleware


def register_user_handlers(user_router: Router):
    user_router.message.middleware(UserActivityMiddleware())
    user_router.callback_query.middleware(UserActivityMiddleware())

    bot_router = Router(name='user_bot_router')
    register_bot_handlers(bot_router)

    other_router = Router(name='user_other_router')
    register_other_handlers(other_router)

    chats_router = Router(name='user_chats_router')
    register_chat_handlers(chats_router)

    user_router.include_routers(bot_router, other_router, chats_router)
