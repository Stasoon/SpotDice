from decimal import Decimal

from .exceptions import BandNotFound, BandTitleAlreadyTaken, AlreadyInOtherBand, UserNotFound
from .models import Band, BandMember, User
from src.misc.enums.leagues import BandLeague
from settings import Config


async def create_band(creator_telegram_id: int, title: str) -> Band | None:
    if await is_band_title_taken(title=title):
        raise BandTitleAlreadyTaken(band_title=title)

    creator: User = await User.get_or_none(telegram_id=creator_telegram_id)
    if not creator:
        return None

    # Создаём новую банду
    band = await Band.create(title=title, league=BandLeague.GAMBLERS, creator=creator)

    # Добавляем создателя в члены банды
    await band.members.add(creator)

    return band


async def get_band_by_id(band_id: int) -> Band | None:
    band = await Band.get_or_none(id=band_id).prefetch_related('creator')
    if not band:
        return None
    return band


async def get_band_by_title(band_title: str) -> Band | None:
    band = await Band.get_or_none(title=band_title)
    if not band:
        return None
    return band


async def get_band_members(band_id: int) -> list[User]:
    band = await Band.get(id=band_id)

    if not band:
        raise BandNotFound(band_id_or_title=band_id)

    members = await band.members.all()
    return members


async def get_sorted_band_members_with_scores(band_id: int) -> list[tuple[User, Decimal]]:
    """
    Возвращает список из кортежей (User, сумма выигранного в банде)
    !!! User содержит только поля 'telegram_id', 'name', 'username', 'balance'
    """
    band = await Band.get(id=band_id)

    if not band:
        raise BandNotFound(band_id_or_title=band_id)

    # Выбираем только необходимые поля из связанных моделей
    members = (
        await User
        .filter(band_members__band=band)
        .order_by('-band_members__score')
        .values('telegram_id', 'name', 'username', 'balance', 'band_members__score')
    )
    return [(User(**member), member['band_members__score']) for member in members]


async def get_bands_global_rating(count: int = 10):
    bands = (
        await Band
        .all()
        .order_by('-score')
        .limit(count)
        .prefetch_related('creator')
    )
    return bands


async def get_bands_rating_in_league(league: BandLeague, count: int = 6):
    bands = (
        await Band
        .filter(league=league)
        .order_by('-score')
        .limit(count)
    )
    return bands


async def get_band_rating_position(target_band: Band) -> int | None:
    # Получаем банду, для которой мы хотим узнать место в рейтинге
    if target_band:
        # Считаем количество банд с более высоким рейтингом
        position = await Band.filter(score__gt=target_band.score).count()

        # Место в рейтинге будет равно position + 1
        return position + 1

    return None


async def get_band_opponents(player_band: Band, count_before: int = 4, count_after: int = 2) -> list[Band]:
    # Получаем банды соперников до и после банды игрока
    opponents_after = await Band.filter(score__lt=player_band.score).order_by('-score').limit(count_before)
    opponents_before = await Band.filter(score__gt=player_band.score).order_by('-score').limit(count_after)

    return sorted(opponents_before + [player_band] + opponents_after, key=lambda x: x.score, reverse=True)


async def get_user_band(telegram_id: int) -> Band | None:
    """ Возвращает банду, в которой состоит игрок """
    user = await User.get_or_none(telegram_id=telegram_id)

    if not user:
        return None

    user_band = await Band.filter(band_members__user__telegram_id=telegram_id).first().prefetch_related('creator')
    return user_band


async def is_user_is_band_creator(band_id: int, user_id: int) -> bool:
    return await Band.filter(id=band_id, creator__telegram_id=user_id).exists()


async def is_band_full(band: Band) -> bool:
    band_members_count = await band.members.all().count()
    return band_members_count >= Config.Bands.BAND_MEMBERS_LIMIT


async def is_band_title_taken(title: str) -> bool:
    title = title.lower()
    # Ищем в базе данных запись с совпадающим названием в нижнем регистре
    band_with_title = await Band.filter(title__iexact=title).first()
    # Если такая запись найдена, возвращаем True (занято), иначе False (не занято)
    return band_with_title is not None


async def add_member_to_band(telegram_id: int, band_id: int | str) -> bool:
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        raise UserNotFound(telegram_id=telegram_id)

    band: Band = await Band.get_or_none(id=band_id)
    if not band:
        raise BandNotFound(band_id_or_title=band_id)

    if await is_band_full(band):
        raise ValueError('В банде нет свободных мест!')

    if await get_user_band(telegram_id=telegram_id):
        raise AlreadyInOtherBand(user=user, band_id_or_title=band_id)

    await band.members.add(user)
    return True


async def update_band_league(band: Band):
    new_league = None

    if band.score >= 2_000_000:
        new_league = BandLeague.MONOPOLISTS
    elif band.score >= 1_000_000:
        new_league = BandLeague.MAGNATES
    elif band.score >= 600_000:
        new_league = BandLeague.INDUSTRIALISTS
    elif band.score >= 200_000:
        new_league = BandLeague.BUSINESSMEN
    elif band.score >= 20_000:
        new_league = BandLeague.CARD_MASTERS
    elif band.score >= 20_000:
        new_league = BandLeague.GAMBLERS

    if new_league and band.league != new_league:
        band.league = new_league
        await band.save()
        await band.on_league_changed(band)


async def update_band_title(band_id: int, new_title: str):
    band = await get_band_by_id(band_id=band_id)
    if not band_id:
        raise BandNotFound(band_id_or_title=band_id)

    band.title = new_title
    await band.save()


async def add_band_win(user_id: int, amount: Decimal):
    band = await get_user_band(telegram_id=user_id)
    if not band:
        return
    band.score += amount
    await band.save()

    await update_band_league(band=band)

    band_member: BandMember = await BandMember.filter(user_id=user_id).first()
    if not band_member:
        return
    band_member.score += amount
    await band_member.save()


async def kick_member_from_band(band_id: int, user_id: int) -> bool:
    band = await get_band_by_id(band_id=band_id)
    user = await User.get_or_none(telegram_id=user_id)
    await band.members.remove(user)
    return True


async def delete_band(band_id: int):
    band = await get_band_by_id(band_id=band_id)
    await band.delete()
