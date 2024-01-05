from decimal import Decimal

from src.database.models import BetRefund, User, Game


async def make_bet_refund(player_id: int, amount: float, game: Game = None):
    """Возврат денег за ставку игрокам"""
    amount = Decimal(amount)
    player = await User.get_or_none(telegram_id=player_id)

    if not player:
        return

    await BetRefund.create(game=game, user=player, amount=amount)
    player.balance += amount
    await player.save()
