from aiogram import Router, F
from aiogram.filters import KICKED, ChatMemberUpdatedFilter
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated

from src.database.users import set_user_blocked_bot
from src.filters import UserExistFilter, MessageIsCommand
from src.messages import GameErrors


# Блокировка бота
async def handle_bot_blocked(event: ChatMemberUpdated):
    await set_user_blocked_bot(user_id=event.from_user.id)


# Срабатывает, если юзер не зарегистрирован в боте и присылает команду
async def handle_not_registered_in_bot_messages(message: Message):
    await message.reply(text=GameErrors.get_not_registered_in_bot())


# Срабатывает, если юзер не зарегистрирован в боте и нажимает кнопку
async def handle_not_registered_in_bot_callbacks(callback: CallbackQuery):
    await callback.answer(text=GameErrors.get_not_registered_in_bot(), show_alert=True)


def register_other_handlers(router: Router):
    router.my_chat_member.filter(F.chat.type == "private")
    router.my_chat_member.register(handle_bot_blocked, ChatMemberUpdatedFilter(member_status_changed=KICKED))

    router.message.register(handle_not_registered_in_bot_messages, MessageIsCommand(), UserExistFilter(False))
    router.callback_query.register(handle_not_registered_in_bot_callbacks, UserExistFilter(False))
