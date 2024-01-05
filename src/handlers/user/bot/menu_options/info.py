from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.keyboards.user import UserMenuKeyboards
from src.messages.user import UserMenuMessages

# region Handlers


async def handle_information_button(message: Message, state: FSMContext):
    await state.clear()

    text = await UserMenuMessages.get_information()
    reply_markup = UserMenuKeyboards.get_information()

    await message.answer_video(caption=text, reply_markup=reply_markup, video=UserMenuMessages.get_information_video())


# endregion


def register_info_handlers(router: Router):
    # ветка Информация
    router.message.register(handle_information_button, F.text.contains('ℹ Информация'))
