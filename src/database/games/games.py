from datetime import datetime
from typing import List, Union
import pytz

from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from tortoise.expressions import Q

from ..models import Game, User, GameStartConfirm
from ..users import get_user_or_none
from src.misc import GameStatus, GameCategory, GameType


# Create
async def create_game(
    creator_telegram_id: int,
    max_players: int,
    game_category: GameCategory,
    game_type: GameType,
    bet: float,
    chat_id: int,
    message_id: int = None,
) -> Game:
    status = GameStatus.ACTIVE if max_players == 1 else GameStatus.WAIT_FOR_PLAYERS
    creator_user = await get_user_or_none(telegram_id=creator_telegram_id)

    game = await Game.create(
        chat_id=chat_id,
        message_id=message_id,
        max_players=max_players,
        creator=creator_user,
        category=game_category,
        game_type=game_type.value,
        status=status.value,
        bet=bet
    )
    await game.players.add(creator_user)
    return game


# Read
async def get_game_obj(game_number: int) -> Game:
    game = await Game.get(number=game_number)
    return game


async def get_creator_of_game(game) -> User:
    try:
        creator = await game.creator.get()
    except MultipleObjectsReturned:
        creator = game.creator
    return creator


async def get_game_by_message_id(chat_id: int, message_id: int) -> Game:
    game = await Game.filter(chat_id=chat_id, message_id=message_id).first()
    return game


async def get_players_of_game(game: Game) -> List[User]:
    return await game.players.all()


async def get_player_ids_of_game(game: Game) -> List[int]:
    """Возвращает список с telegram id игроков"""
    return await game.players.all().values_list('telegram_id', flat=True)


async def is_game_full(game: Game) -> bool:
    """Возвращает True, если все игроки собраны"""
    players_count = await game.players.all().count()
    return True if players_count >= game.max_players else False


async def get_chat_available_games(chat_id: int) -> Union[List[Game], None]:
    """Возвращает игры из конкретного чата с состоянием WAIT_FOR_PLAYERS"""
    try:
        return await Game.filter(status=GameStatus.WAIT_FOR_PLAYERS, chat_id=chat_id)
    except DoesNotExist:
        return None


async def get_bot_available_games(
        game_category: GameCategory,
        offset: int = 0,
        limit: int = 8,
        for_user_id: int = None
) -> List[Game]:
    """Возвращает доступные для вступления игры конкретной категории, созданные в боте"""
    # Немного костыльно, тк chat_id игр, созданных в боте равен id юзера, а оно всегда положительное
    games = await Game.filter(
        status=GameStatus.WAIT_FOR_PLAYERS, category=game_category, chat_id__gt=0
    ).offset(offset).limit(limit)

    # Если есть игра пользователя, переместите ее в начало списка
    if for_user_id and len(games) != 0:
        user_game = await get_user_unfinished_game(telegram_id=for_user_id)
        if user_game and user_game.category == game_category:
            if user_game in games:
                games.remove(user_game)
            games.insert(0, user_game)

    return games


async def get_user_unfinished_game(telegram_id: int) -> Game | None:
    """Возвращает незаконченную игру юзера (если статус - ACTIVE или WAIT_FOR_PLAYERS)"""
    user = await User.get_or_none(telegram_id=telegram_id)

    if not user:
        return

    await user.fetch_related('games_participated')
    game = await user.games_participated.filter(
        (Q(status=GameStatus.ACTIVE) | Q(status=GameStatus.WAIT_FOR_PLAYERS) | Q(status=GameStatus.WAIT_FOR_CONFIRM))
        & Q(players=user)
    ).first()

    return game if game else None


async def get_user_active_game(telegram_id: int) -> Game | None:
    """Возвращает активную игру юзера (если статус - ACTIVE)"""
    user = await User.get_or_none(telegram_id=telegram_id)
    await user.fetch_related('games_participated')
    game = await user.games_participated.filter(
        (Q(status=GameStatus.ACTIVE) | Q(status=GameStatus.WAIT_FOR_CONFIRM)) & Q(players=user)
    ).all().first()

    return game if game else None


async def get_total_games_count() -> int:
    """Возвращает число с количеством игр в БД за всё время"""
    return await Game.all().count()


# Update

async def add_user_to_game(telegram_id: int, game_number: int) -> bool:
    user = await User.get(telegram_id=telegram_id)
    game = await Game.get(number=game_number)

    if await game.players.all().count() < game.max_players:
        await game.players.add(user)
        return True
    else:
        return False


async def update_message_id(game: Game, new_message_id: int):
    """Обновить id стартового сообщения игры"""
    game.message_id = new_message_id
    await game.save()


async def finish_game(game: Game) -> None:
    game.status = GameStatus.FINISHED
    await game.save()
    await GameStartConfirm.filter(game=game).delete()


async def cancel_game(game: Game):
    game.status = GameStatus.CANCELLED
    await game.save()
    await GameStartConfirm.filter(game=game).delete()


async def activate_game(game: Game):
    game.status = GameStatus.ACTIVE
    await game.save()


async def set_wait_for_confirm_status(game: Game):
    game.status = GameStatus.WAIT_FOR_CONFIRM
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    game.time_started = utc_now
    await game.save()

