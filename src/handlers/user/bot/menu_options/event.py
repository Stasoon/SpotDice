from aiogram import Router, F
from aiogram.types import Message

from src.messages import UserMenuMessages
from src.keyboards.user import UserMenuKeyboards


async def handle_events_button(message: Message):
    await message.answer(text=UserMenuMessages.get_events(), reply_markup=UserMenuKeyboards.get_events())


def register_events_handlers(router: Router):
    router.message.register(handle_events_button, F.text.lower().contains('события'))
