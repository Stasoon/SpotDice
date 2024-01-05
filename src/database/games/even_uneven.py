from ..models import EvenUnevenPlayerBet
from ...misc.enums.games_enums import EvenUnevenBetOption


async def add_player_bet(player_id: int, amount: float, option: EvenUnevenBetOption):
    await EvenUnevenPlayerBet.create(player_id=player_id, amount=amount, option=option)


async def delete_player_bet(player_id: int):
    await EvenUnevenPlayerBet.filter(player_id=player_id).delete()


async def get_players_bets() -> list[EvenUnevenPlayerBet]:
    return await EvenUnevenPlayerBet.all()
