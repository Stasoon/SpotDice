from typing import Literal

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import (InlineKeyboardMarkup, InlineKeyboardBuilder)

from src.misc import (
    MenuNavigationCallback, DepositCheckCallback,
    ConfirmWithdrawRequisitesCallback, DepositMethod, DepositCallback, WithdrawCallback, WithdrawMethod
)
from src.utils import cryptobot


class UserPaymentKeyboards:
    @staticmethod
    def get_cancel_payment() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True,
            is_persistent=True
        )

    @staticmethod
    def get_deposit_methods() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру с методами пополнения"""
        builder = InlineKeyboardBuilder()

        builder.button(text='💳 Карта / СБП', callback_data=DepositCallback(method=DepositMethod.SBP))
        builder.button(text='🤖 КриптоБот', callback_data=DepositCallback(method=DepositMethod.CRYPTO_BOT))
        builder.button(text='💜 ЮMoney', callback_data=DepositCallback(method=DepositMethod.U_MONEY))
        # builder.button(text='🥝 Киви', callback_data=DepositCallback(method=DepositMethod.QIWI))

        builder.adjust(2)
        back_builder = InlineKeyboardBuilder()
        back_builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='profile'))
        return builder.attach(back_builder).as_markup()

    @staticmethod
    def get_withdraw_methods() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру с методами вывода"""
        builder = InlineKeyboardBuilder()

        builder.button(text='💳 Карта / СБП', callback_data=WithdrawCallback(method=WithdrawMethod.SBP))
        builder.button(text='🤖 КриптоБот', callback_data=WithdrawCallback(method=WithdrawMethod.CRYPTO_BOT))
        builder.button(text='💜 ЮMoney', callback_data=WithdrawCallback(method=WithdrawMethod.U_MONEY))

        builder.adjust(2)
        back_builder = InlineKeyboardBuilder()
        back_builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='profile'))
        return builder.attach(back_builder).as_markup()

    @staticmethod
    def get_confirm_withdraw_requisites() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='✅ Отправить', callback_data=ConfirmWithdrawRequisitesCallback(requisites_correct=True))
        builder.button(
            text='✏ Изменить реквизиты', callback_data=ConfirmWithdrawRequisitesCallback(requisites_correct=False))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def get_crypto_bot_choose_currency(transaction_type: Literal['deposit', 'withdraw']) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, которая должна отображаться после нажатия на метод оплаты Крипто Ботом"""
        currency_builder = InlineKeyboardBuilder()

        currencies = await cryptobot.get_currencies()
        for currency_code in currencies:
            callback_data = DepositCallback if transaction_type == 'deposit' else WithdrawCallback
            method = DepositMethod.CRYPTO_BOT if transaction_type == 'deposit' else WithdrawMethod.CRYPTO_BOT
            currency_builder.button(
                text=currency_code, callback_data=callback_data(currency=currency_code, method=method)
            )
        currency_builder.adjust(4)

        back_builder = InlineKeyboardBuilder()
        back_builder.button(text='🔙 Отмена', callback_data=MenuNavigationCallback(branch='profile', option='deposit'))
        back_builder.adjust(1)

        currency_builder.attach(back_builder)
        return currency_builder.as_markup()

    @staticmethod
    def get_invoice(method: DepositMethod, pay_url: str, invoice_id: int) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру для оплаты и её проверки"""
        builder = InlineKeyboardBuilder()
        builder.button(text='Оплатить', url=pay_url)
        builder.button(text='Проверить', callback_data=DepositCheckCallback(method=method, invoice_id=invoice_id))
        builder.adjust(1)
        return builder.as_markup()
