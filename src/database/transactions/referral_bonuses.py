from decimal import Decimal

from tortoise.functions import Sum

from ..models import ReferralBonus
from ..users import get_referrer_id_of_user, get_user_or_none, get_referrals_count_by_telegram_id


async def calculate_referral_bonus_percent(user_id: int) -> float:
    referrals_count = await get_referrals_count_by_telegram_id(user_id=user_id)

    if referrals_count < 50:
        multiplier = 2
    elif 50 <= referrals_count < 100:
        multiplier = 2.5
    elif 100 <= referrals_count < 170:
        multiplier = 3
    elif 170 <= referrals_count < 300:
        multiplier = 4
    else:  # referrals_count >= 300
        multiplier = 5

    return multiplier/100


async def accrue_referral_bonus(referred_user_id: int, game_winning_amount: Decimal):
    """Начислить реферальный бонус"""
    referrer_id = await get_referrer_id_of_user(user_id=referred_user_id)
    referrer = await get_user_or_none(referrer_id)

    if not referrer:
        return

    # Высчитываем сумму бонуса
    multiplier = await calculate_referral_bonus_percent(user_id=referrer_id)
    referral_bonus = game_winning_amount * Decimal(multiplier)

    # Начисляем бонус тому, кто пригласил юзера
    referrer.balance += referral_bonus
    await referrer.save()

    # Создаем запись о начислении бонуса в таблице транзакций
    await ReferralBonus.create(
        recipient=referrer,
        referral_id=referred_user_id,
        amount=referral_bonus
    )


async def get_referral_earnings(user_telegram_id: int) -> float:
    """Получить сумму, полученную от рефералов"""
    deposit_amount = await ReferralBonus.filter(
        recipient_id=user_telegram_id
    ).annotate(total_amount=Sum('amount')).values_list('total_amount')

    deposits_sum = deposit_amount[0][0]
    return deposits_sum if deposits_sum else 0.0
