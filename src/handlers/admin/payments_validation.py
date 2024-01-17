from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramAPIError

from src.filters import IsAdminFilter
from src.misc import AdminValidatePaymentCallback
from src.database.transactions import deposit_to_user


async def handle_validate_payment_callback(callback: CallbackQuery, callback_data: AdminValidatePaymentCallback):
    try:
        await callback.message.edit_reply_markup()
    except TelegramAPIError:
        await callback.message.delete()
        await callback.bot.copy_message(
            chat_id=callback.message.chat.id,
            from_chat_id=callback.message.chat.id,
            message_id=callback.message.message_id
        )

    transaction_word = 'пополнение' if callback_data.transaction_type == 'deposit' else 'вывод'

    if callback_data.confirm is False:  # Если отмена
        await callback.bot.send_message(
            callback_data.user_id,
            text=f'❌ Ваша заявка на {transaction_word} {callback_data.amount}₽ была отклонена. \n\n'
                 f'Если считаете, что это ошибка - обратитесь к администратору: @helperdicy'
        )

        # Если был вывод, возвращаем средства
        if callback_data.transaction_type == 'withdraw':
            await deposit_to_user(user_id=callback_data.user_id, amount=callback_data.amount, create_record=False)
            return
        return
    else:  # Если подтвердили
        await callback.bot.send_message(
            callback_data.user_id,
            text=f'✅ Ваша заявка на {transaction_word} {callback_data.amount}₽ была выполнена.'
        )

        if callback_data.transaction_type == 'deposit':
            await deposit_to_user(
                user_id=callback_data.user_id, amount=callback_data.amount,
                method=callback_data.method, create_record=True
            )


def register_validate_request_handlers(router: Router):
    router.callback_query.register(
        handle_validate_payment_callback,
        AdminValidatePaymentCallback.filter(),
        IsAdminFilter(True)
    )

