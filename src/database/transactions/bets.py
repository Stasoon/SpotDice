from decimal import Decimal

from tortoise.functions import Sum

from src.database.models import Bet, User, Game


async def deduct_bet_from_user_balance(user_telegram_id: int, amount: float, game: Game = None):
    """Списание ставки с баланса"""
    amount = Decimal(amount)
    user = await User.get(telegram_id=user_telegram_id)

    if 0 < amount <= user.balance:
        user.balance -= amount
        await user.save()

        transaction = await Bet.create(game=game, user=user, amount=amount)
        return transaction
    else:
        return None


async def get_total_bets_sum():
    total_bets_sum = (
        await Bet
        .all()
        .annotate(bets_sum=Sum('amount'))
        .values()
    )
    return float(total_bets_sum[0]['bets_sum'] if total_bets_sum else 0)
