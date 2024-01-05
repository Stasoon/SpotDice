from decimal import Decimal

from tortoise.functions import Sum

from ..models import User, Deposit
from ...misc import DepositMethod


async def deposit_to_user(
        user_id: int, amount: float, method: DepositMethod = None, create_record: bool = True
) -> Deposit | None:
    """ Начислить депозит юзеру """
    amount = Decimal(amount)
    user = await User.get_or_none(telegram_id=user_id)

    if not user:
        return None

    user.balance += amount
    await user.save()

    if create_record:
        deposit = await Deposit.create(user=user, amount=amount, method=method)
        return deposit
    return None


async def get_user_all_deposits_sum(user: User) -> float:
    """Получение суммы пополнений пользователя"""
    deposit_amount = await Deposit.filter(
        user=user
    ).annotate(total_amount=Sum('amount')).values_list('total_amount')

    deposits_sum = deposit_amount[0][0]
    return deposits_sum if deposits_sum else 0.0
