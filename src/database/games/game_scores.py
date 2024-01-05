from tortoise.exceptions import DoesNotExist

from ..models import PlayerScore, Game


# Create
async def add_player_move_if_not_moved(game: Game, player_telegram_id: int, move_value: int) -> None:
    await PlayerScore.get_or_create(game=game, player_id=player_telegram_id, defaults={'value': move_value})


# Read
async def get_game_moves(game: Game) -> list[PlayerScore]:
    moves = await PlayerScore.filter(game=game).all()
    return moves


async def is_all_players_moved(game: Game) -> bool:
    moves_count = await PlayerScore.filter(game=game).count()
    return moves_count == game.max_players


# Delete
async def delete_game_scores(game: Game) -> None:
    try:
        await PlayerScore.filter(game=game).delete()
    except DoesNotExist:
        pass
