from datetime import datetime
from typing import Literal

from aiogram import html

from src.database.models import PromoCode, ReferralLink
from src.misc import WithdrawMethod, DepositMethod
from src.utils.text_utils import format_float_to_rub_string


class AdminMessages:

    @staticmethod
    def get_deposit_request(
            transaction_type: Literal['deposit', 'withdraw'],
            user_id: int,
            amount: float,
            user_name: str = 'Пользователь',
            user_requisites: str = None,
            method: DepositMethod | WithdrawMethod = None
    ):

        if transaction_type == 'deposit':
            transaction_str = f'➕ Пополнение баланса ➕'
        else:
            transaction_str = f'➖ Вывод средств ➖'
        user_requisites_str = f'💳 Реквизиты: \n<code>{user_requisites}</code> \n' if user_requisites else ''

        return f'{html.bold(transaction_str)} \n\n' \
               f'👤 {html.link(f"{user_name}", f"tg://user?id={user_id}")} \n' \
               f'🆔 {html.code(user_id)} \n\n' \
               f'📆 {html.italic(datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M"))} \n' \
               f'🏦 Метод: {method.value} \n' \
               f'{user_requisites_str}' \
               f'💵 Сумма: {format_float_to_rub_string(amount)}'

    @staticmethod
    def get_bonus_description(bonus: PromoCode) -> str:
        text = (
            f'🎁 Бонус\n\n'
            f'Сумма: {format_float_to_rub_string(bonus.amount)} \n'
            f'Код активации: <code>{bonus.activation_code}</code> \n'
            f'Количество активаций: {bonus.total_activations_count} \n'
            f'Осталось использований: {bonus.remaining_activations_count} \n'
            f'Использован раз: {bonus.total_activations_count - bonus.remaining_activations_count} \n'
        )
        return text

    @staticmethod
    def get_referral_links_list(bot_username: str, referral_links: list[ReferralLink]) -> str:
        text = '🔗 Реферальные ссылки \n\n' \
               '<b>Список реферальных ссылок:</b> \n\n'

        for n, link in enumerate(referral_links, start=1):
            text += (
                f'{n} — <code>{link.name}</code> \n'
                f'🔗 <code>https://t.me/{bot_username}?start={link.name}</code> \n'
                f'📊 Кол-во переходов: {link.user_count} \n'
                # f'📲 На ОП подписались: {link.passed_op_count} \n'
            )
            text += '-' * 30 + '\n'
        return text

