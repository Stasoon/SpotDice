from src.database.models import MinesGameData, User, Game


async def create(user: User, game: Game, mines_count: int) -> MinesGameData:
    await MinesGameData.filter(player=user).delete()
    data = await MinesGameData.create(player=user, game=game, mines_count=mines_count)
    return data


async def get(user: User) -> MinesGameData | None:
    return await MinesGameData.filter(player=user).first().prefetch_related('game')


async def increase_opened_cells(data: MinesGameData) -> int:
    data.cells_opened += 1
    await data.save()
    return data.cells_opened


async def delete(user: User):
    await MinesGameData.filter(player=user).delete()
