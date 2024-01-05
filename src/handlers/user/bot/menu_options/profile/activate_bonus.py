import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.database import bonuses, users
from src.keyboards import UserMenuKeyboards
from src.messages import UserMenuMessages
from src.misc import MenuNavigationCallback
from src.misc.states import ActivateBonusStates
from src.utils.text_utils import format_float_to_rub_string


async def handle_cancel_bonus_activation(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Активация бонуса отменена', reply_markup=UserMenuKeyboards.get_main_menu())

    user = await users.get_user_or_none(message.from_user.id)
    text = await UserMenuMessages.get_profile(user)
    reply_markup = UserMenuKeyboards.get_profile()
    await message.answer(text=text, reply_markup=reply_markup)


async def handle_activate_bonus_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text='<b>✍🏻 Введите ваш промокод:</b>', reply_markup=UserMenuKeyboards.get_cancel_reply()
    )
    await state.set_state(ActivateBonusStates.wait_for_code)


async def handle_bonus_code_message(message: Message, state: FSMContext):
    bonus = await bonuses.get_bonus_by_activation_code_or_none(code=message.text)
    user = await users.get_user_or_none(telegram_id=message.from_user.id)

    error_text = ''
    if not bonus:
        error_text = '❗Промокод не найден'
    elif user.balance > 0:
        error_text = '❗Промокод является без депозитным'
    elif not bonus.is_active:
        error_text = '❗Количество активаций промокода исчерпано'
    elif await bonuses.is_user_activated_bonus(user=user, bonus=bonus):
        error_text = '❗Вы уже активировали этот бонус ранее'

    if error_text:
        await message.answer(text=error_text, reply_markup=UserMenuKeyboards.get_main_menu())
    else:
        await bonuses.make_activation(bonus=bonus, user=user)
        await message.answer(
            text=f'🎊 Бонус в {format_float_to_rub_string(bonus.amount)} активирован!',
            reply_markup=UserMenuKeyboards.get_main_menu()
        )

    await state.clear()
    await asyncio.sleep(1)
    user = await users.get_user_or_none(message.from_user.id)
    text = await UserMenuMessages.get_profile(user)
    reply_markup = UserMenuKeyboards.get_profile()
    await message.answer(text=text, reply_markup=reply_markup)


def register_activate_bonus_handlers(router: Router):
    # обработка кнопки отмены активации
    router.message.register(
        handle_cancel_bonus_activation, F.text == '❌ Отмена', StateFilter(ActivateBonusStates)
    )

    # кнопка активировать бонус
    router.callback_query.register(
        handle_activate_bonus_callback,
        MenuNavigationCallback.filter((F.branch == 'profile') & (F.option == 'bonus'))
    )

    router.message.register(handle_bonus_code_message, ActivateBonusStates.wait_for_code)
