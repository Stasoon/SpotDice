from tortoise.exceptions import DoesNotExist
from tortoise.functions import Sum

from ..models import PlayingCard


DEALER_ID = 0


# Create
async def add_card_to_player_hand(
    game_number: int, player_telegram_id: int,
    card_suit, card_value,
    points: int = 0
):
    await PlayingCard.create(
        game_id=game_number,
        player_id=player_telegram_id,
        suit=card_suit,
        value=card_value,
        points=points
    )


async def add_card_to_dealer_hand(game_number: int, card_suit, card_value, points: int = 0):
    await add_card_to_player_hand(
        game_number=game_number, player_telegram_id=DEALER_ID,
        card_suit=card_suit, card_value=card_value, points=points
    )


# Read

async def get_player_cards(game_number: int, player_id: int) -> list[PlayingCard]:
    moves = await PlayingCard.filter(game_id=game_number, player_id=player_id).all()
    return moves


async def get_dealer_cards(game_number: int):
    return await get_player_cards(game_number=game_number, player_id=DEALER_ID)


async def count_player_score(game_number: int, player_id: int) -> int:
    score = await PlayingCard.filter(game_id=game_number, player_id=player_id).annotate(
        score=Sum('points')
    ).values_list('score')
    return score[0][0]


async def count_dealer_score(game_number: int) -> int:
    return await count_player_score(game_number=game_number, player_id=DEALER_ID)


# Delete
async def delete_player_cards(game_number: int, user_id: int) -> None:
    try:
        await PlayingCard.filter(game_id=game_number, player_id=user_id).delete()
    except DoesNotExist:
        pass


async def delete_dealer_cards(game_number: int) -> None:
    await delete_player_cards(game_number=game_number, user_id=DEALER_ID)


async def delete_game_cards(game_number: int) -> None:
    try:
        await PlayingCard.filter(game_id=game_number).delete()
    except DoesNotExist:
        pass

