from datetime import datetime, timedelta
from decimal import Decimal

from tortoise.functions import Sum, Count

from settings import Config
from .referral_bonuses import accrue_referral_bonus
from ..bands import add_band_win
from ..models import User, Winning
from src.misc import GameCategory
from src.utils import logger


async def accrue_winnings(winner_telegram_id: int, amount: float, game_category: GameCategory) -> float:
    """
    Начисление выигрыша победителю и процента пригласившему.
    Возвращает выигрыш с учётом комиссии
    """
    if amount <= 0:
        return 0

    winning_commission = Decimal(1 - Config.Payments.winning_commission)
    amount_with_commission = Decimal(amount) * winning_commission

    try:
        user = await User.get(telegram_id=winner_telegram_id)
        user.balance += amount_with_commission
        await user.save()
        await Winning.create(user=user, amount=amount_with_commission, game_category=game_category)

        # увеличиваем баланс того, кто пригласил
        await accrue_referral_bonus(referred_user_id=winner_telegram_id, game_winning_amount=amount_with_commission)
        await add_band_win(user_id=winner_telegram_id, amount=amount_with_commission)
        return float(amount_with_commission)
    except Exception as e:
        logger.error(e)


async def get_top_winners_by_amount(category: GameCategory, days_back: int = None, limit: int = 3) -> list[User]:
    """Возвращает топ по суммам выигрыша в виде списка User с добавленным полем winnings_amount"""
    if days_back is None:
        start_date = datetime.min  # Установите начальную дату как 0 дней назад
    else:
        # Вычисляем дату, до которой нужно учитывать транзакции (сегодня - days_back дней)
        start_date = datetime.now() - timedelta(days=days_back)

    top_players = await User.filter(
        user_winnings__timestamp__gte=start_date,
        user_winnings__game_category=category
    ).annotate(
        winnings_amount=Sum('user_winnings__amount')
    ).order_by('-winnings_amount').limit(limit)

    return top_players


async def get_top_winners_by_count(days_back: int = None, limit: int = 10) -> list[User]:
    """Возвращает топ по количеству выигрышей в виде списка User с добавленным полем wins_count"""
    if days_back is None:
        start_date = datetime.min  # Установите начальную дату как 0 дней назад
    else:
        # Вычисляем дату, до которой нужно учитывать транзакции (сегодня - days_back дней)
        start_date = datetime.now() - timedelta(days=days_back)

    top_players = await User.filter(
        user_winnings__timestamp__gte=start_date
    ).annotate(
        wins_count=Count('user_winnings')
    ).order_by('-wins_count').limit(limit)

    return top_players
