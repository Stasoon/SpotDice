from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.database import users
from src.keyboards.user import UserMenuKeyboards
from src.messages import UserMenuMessages
from src.misc import (MenuNavigationCallback)
from .activate_bonus import register_activate_bonus_handlers
from .deposit import register_deposit_handlers
from .withdraw import register_withdraw_handlers


# region Utils

async def get_profile_message_data(user_id: int) -> dict:
    user = await users.get_user_or_none(user_id)
    text = await UserMenuMessages.get_profile(user)
    photo = UserMenuMessages.get_profile_photo()
    reply_markup = UserMenuKeyboards.get_profile()
    return {'photo': photo, 'caption': text, 'reply_markup': reply_markup}


async def edit_message_to_profile(user_id: int, message: Message) -> None:
    user = await users.get_user_or_none(user_id)
    text = await UserMenuMessages.get_profile(user)
    photo = UserMenuMessages.get_profile_photo()
    reply_markup = UserMenuKeyboards.get_profile()

    if message.photo:
        await message.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await message.answer_photo(photo=photo, caption=text, reply_markup=reply_markup)
        await message.delete()
    # return {'caption': text, 'reply_markup': reply_markup}


# endregion


# region Handlers


async def handle_profile_button(message: Message, state: FSMContext):
    """Показывает сообщение по нажатию на кнопку Профиль"""
    await state.clear()
    msg_data = await get_profile_message_data(message.from_user.id)
    await message.answer_photo(**msg_data)


# Реферальная система
async def handle_referral_system_callback(callback: CallbackQuery):
    """Показывает сообщение по нажатию на кнопку Реферальная система"""
    bot_username = (await callback.bot.get_me()).username
    user_id = callback.from_user.id
    await callback.message.edit_caption(
        caption=await UserMenuMessages.get_referral_system(bot_username, user_id),
        reply_markup=UserMenuKeyboards.get_referral_system(bot_username, user_id)
    )


# обработка кнопок Назад
async def handle_back_in_profile_callbacks(callback: CallbackQuery):
    """Обработка нажатия на кнопку назад в Профиль"""
    await edit_message_to_profile(user_id=callback.from_user.id, message=callback.message)
    # await callback.message.edit_caption(**(await get_profile_message_data(callback.from_user.id)))


# endregion


def register_profile_handlers(router: Router):
    # обработка кнопки Профиль
    router.message.register(handle_profile_button, F.text.lower().contains('профиль'))

    # опция Реферальная система
    router.callback_query.register(
        handle_referral_system_callback,
        MenuNavigationCallback.filter((F.branch == 'profile') & (F.option == 'referral_system'))
    )

    # кнопка назад в Профиль
    router.callback_query.register(
        handle_back_in_profile_callbacks,
        MenuNavigationCallback.filter((F.branch == 'profile') & ~F.option)
    )

    register_deposit_handlers(router)
    register_withdraw_handlers(router)
    register_activate_bonus_handlers(router)
