from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from settings import Config
from src.database import users
from src.keyboards.user import UserMenuKeyboards, UserPaymentKeyboards
from src.messages import UserPaymentMessages, InputErrors, BalanceErrors
from src.misc import (MenuNavigationCallback, WithdrawCallback, WithdrawMethod,
                      ConfirmWithdrawRequisitesCallback)
from src.misc.states import HalfAutoWithdrawStates
from src.utils import post_payment
from src.database.transactions import withdraw_balance


# region Utils

async def validate_and_get_transaction_amount(amount_message: Message) -> float | None:
    try:
        transaction_amount = float(amount_message.text)
    except (ValueError, TypeError):
        await amount_message.answer(InputErrors.get_message_not_number_retry(), parse_mode='HTML')
        return None

    min_transaction_amount = Config.Payments.min_withdraw_amount
    user_balance = await users.get_user_balance(amount_message.from_user.id)

    if transaction_amount > user_balance:
        await amount_message.answer(
            text=BalanceErrors.get_insufficient_balance(user_balance),
            parse_mode='HTML')
        return None
    elif transaction_amount < min_transaction_amount:
        await amount_message.answer(
            text=BalanceErrors.get_insufficient_transaction_amount(min_transaction_amount)
        )
        return

    return transaction_amount

# endregion


async def handle_cancel_withdraw(message: Message, state: FSMContext):
    """ Обработка нажатия на кнопку отмены вывода средств """
    await state.clear()
    await message.answer(
        text=UserPaymentMessages.get_withdrawing_canceled(), reply_markup=UserMenuKeyboards.get_main_menu())
    await message.answer(
        text=UserPaymentMessages.get_choose_withdraw_method(), reply_markup=UserPaymentKeyboards.get_withdraw_methods())


async def handle_withdraw_callback(callback: CallbackQuery):
    """Обработка нажатия на кнопку Вывода средств"""
    min_withdraw_amount = Config.Payments.min_withdraw_amount

    if await users.get_user_balance(callback.from_user.id) < min_withdraw_amount:
        await callback.answer(text=BalanceErrors.low_balance_for_withdraw(min_withdraw_amount), show_alert=True)
        return

    await callback.message.edit_text(
        text=UserPaymentMessages.get_choose_withdraw_method(),
        reply_markup=UserPaymentKeyboards.get_withdraw_methods(),
        parse_mode='HTML'
    )


async def handle_show_withdraw_method_callbacks(
        callback: CallbackQuery, callback_data: WithdrawCallback, state: FSMContext
):
    """Обработка нажатия на метод вывода средств"""
    await state.update_data(method=callback_data.method)

    # если метод вывода - криптобот
    if callback_data.method == WithdrawMethod.CRYPTO_BOT:
        text = UserPaymentMessages.choose_currency()
        markup = await UserPaymentKeyboards.get_crypto_bot_choose_currency(transaction_type='withdraw')
        await callback.message.edit_text(text=text, reply_markup=markup, parse_mode='HTML')

    # если метод вывода полуавтоматический
    elif callback_data.method in (WithdrawMethod.SBP, WithdrawMethod.U_MONEY):
        await callback.message.delete()
        text = UserPaymentMessages.enter_withdraw_amount(min_withdraw_amount=Config.Payments.min_withdraw_amount)
        markup = UserPaymentKeyboards.get_cancel_payment()
        await callback.message.answer(text=text, reply_markup=markup, parse_mode='HTML')
        await state.set_state(HalfAutoWithdrawStates.wait_for_amount)


async def handle_withdraw_amount_message(message: Message, state: FSMContext):
    withdraw_amount = await validate_and_get_transaction_amount(message)
    if not withdraw_amount:
        return

    data = await state.get_data()

    if withdraw_amount:
        await message.answer(UserPaymentMessages.enter_user_withdraw_requisites(data.get('method')),
                             parse_mode='HTML')
        await state.update_data(amount=withdraw_amount)
        await state.set_state(HalfAutoWithdrawStates.wait_for_requisites)


async def handle_user_withdraw_requisites(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(InputErrors.get_text_expected_retry(), parse_mode='HTML')
        return
    elif len(message.text) > 80:
        await message.answer(InputErrors.get_message_text_too_long_retry(), parse_mode='HTML')
        return
    elif len(message.text) < 8:
        await message.answer(InputErrors.get_message_text_too_short_retry(), parse_mode='HTML')
        return

    await message.answer(UserPaymentMessages.get_confirm_withdraw_requisites(),
                         reply_markup=UserPaymentKeyboards.get_confirm_withdraw_requisites(),
                         parse_mode='HTML')
    await state.update_data(requisites=message.text)
    await state.set_state(HalfAutoWithdrawStates.wait_for_confirm)


async def handle_confirm_withdraw_callback(
        callback: CallbackQuery, callback_data: ConfirmWithdrawRequisitesCallback, state: FSMContext
):
    data = await state.get_data()

    # кнопка редактирования реквизитов
    if not callback_data.requisites_correct:
        await callback.message.edit_text(
            text=UserPaymentMessages.enter_user_withdraw_requisites(data.get('method')), parse_mode='HTML'
        )
        await state.set_state(HalfAutoWithdrawStates.wait_for_requisites)
        return

    # иначе делаем списание и пост в канал с чеками
    await withdraw_balance(user_id=callback.from_user.id, amount=data.get('amount'), method=data.get('method'))

    await post_payment.send_payment_request_to_admin(
        bot=callback.bot,
        user_id=callback.from_user.id, user_name=callback.from_user.full_name,
        amount=data.get('amount'),
        transaction_type='withdraw',
        method=data.get('method'),
        requisites=data.get('requisites')
    )

    await callback.message.delete()
    await callback.message.answer(
        text=UserPaymentMessages.get_wait_for_administration_confirm(),
        reply_markup=UserMenuKeyboards.get_main_menu(),
        parse_mode='HTML'
    )
    await state.clear()


def register_withdraw_handlers(router: Router):
    # обработка кнопки отмены вывода средств
    router.message.register(
        handle_cancel_withdraw, F.text == '❌ Отмена', StateFilter(HalfAutoWithdrawStates)
    )

    # опция Вывод средств
    router.callback_query.register(
        handle_withdraw_callback, MenuNavigationCallback.filter((F.branch == 'profile') & (F.option == 'withdraw'))
    )

    # Методы вывода средств
    router.callback_query.register(handle_show_withdraw_method_callbacks, WithdrawCallback.filter(~F.currency))

    # Сообщение с суммой вывода
    router.message.register(handle_withdraw_amount_message, HalfAutoWithdrawStates.wait_for_amount)

    # Ввод реквизитов, на которые выводить деньги
    router.message.register(handle_user_withdraw_requisites, HalfAutoWithdrawStates.wait_for_requisites)

    # Подтверждение реквизитов
    router.callback_query.register(
        handle_confirm_withdraw_callback,
        HalfAutoWithdrawStates.wait_for_confirm,
        ConfirmWithdrawRequisitesCallback.filter()
    )
