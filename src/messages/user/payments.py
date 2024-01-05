from aiogram import html

from src.misc import WithdrawMethod, DepositMethod
from src.utils.text_utils import format_float_to_rub_string


class UserPaymentMessages:
    @staticmethod
    def get_depositing_canceled() -> str:
        return "Пополнение баланса отменено"

    @staticmethod
    def get_withdrawing_canceled() -> str:
        return "Вывод средств с баланса отменён"

    @staticmethod
    def get_choose_deposit_method() -> str:
        return html.bold('💎 Выберите способ пополнения баланса:')

    @staticmethod
    def get_choose_withdraw_method() -> str:
        return html.bold('💎 Выберите способ вывода средств с баланса:')

    @staticmethod
    def get_confirm_withdraw_requisites() -> str:
        return '💎 Отправить заявку на вывод?'

    @staticmethod
    def choose_currency() -> str:
        return html.bold('💎 Выберите валюту:')

    @staticmethod
    def ask_for_deposit_amount(min_deposit_amount: float = None) -> str:
        """
        Возвращает текст с просьбой ввести сумму депозита. \n
        min_deposit_amount: если указано, добавляет строку с минимальной суммой
        """
        text = html.bold(f"💎 Введите, сколько рублей вы хотите внести: \n")
        if min_deposit_amount:
            text += f"(Минимальный депозит - {format_float_to_rub_string(min_deposit_amount)})"
        return text

    @staticmethod
    def enter_withdraw_amount(min_withdraw_amount) -> str:
        return html.bold("💎 Введите, сколько рублей вы хотите вывести с баланса: \n") + \
               f"(Минимальная сумма вывода - {format_float_to_rub_string(min_withdraw_amount)})"

    @staticmethod
    def enter_user_withdraw_requisites(withdraw_method: WithdrawMethod) -> str:
        """Возвращает строку с просьбой ввести реквизиты пользователя, на которые нужно переводить деньги,
        в зависимости от метода"""
        necessary_requisites = None

        if withdraw_method == WithdrawMethod.SBP:
            necessary_requisites = f"💳 Введите {html.bold('название банка')} и {html.bold('номер телефона/карты')}:"
        elif withdraw_method == WithdrawMethod.U_MONEY:
            necessary_requisites = f"💳 Введите ваш {html.bold('номер кошелька ЮMoney')}:"
        return necessary_requisites

    @staticmethod
    def get_half_auto_deposit_method_requisites(deposit_method: DepositMethod):
        """Возвращает реквизиты владельца в зависимости от метода"""
        requisites = ''

        match deposit_method:
            case DepositMethod.SBP:
                requisites = "📩 Отправьте деньги по СБП по реквизитам: \n" \
                             f"💳 По номеру телефона/карты: \n" \
                             f"Тинькофф: <code>4377 7278 1387 3135</code>\n" \
                             f"Сбербанк: <code>4276 4200 4964 6879</code> \n" \
                             f"Номер телефона, привязанный к банкам: <code>+79056671283</code>"
            case DepositMethod.U_MONEY:
                requisites = "📩 Отправьте деньги на ЮMoney по реквизитам: \n" \
                             f"💳 По номеру счёта: \n{html.code('0000000000000000')}"
            # case DepositMethod.QIWI:
            #     requisites = "📩 Отправьте деньги на Qiwi по реквизитам: \n" \
            #                  f"💳 По номеру счёта: \n{html.code('4890494766966584')}"

        requisites += '\n\n📷 Отправьте боту скриншот чека:'
        return requisites

    @staticmethod
    def get_deposit_link_message() -> str:
        return "🔗 Вот ссылка на пополнение:"

    @staticmethod
    def get_deposit_confirmed() -> str:
        return '✅ Готово! Сумма начислена на ваш баланс.'

    @staticmethod
    def get_wait_for_administration_confirm() -> str:
        return '✅ Заявка создана \n\n⏰ Ожидайте рассмотрения...'
