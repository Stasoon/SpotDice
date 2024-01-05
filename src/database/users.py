from datetime import datetime, timedelta
from typing import AsyncGenerator, Union

from tortoise.exceptions import DoesNotExist

from .models import User


# Create
async def create_user_if_not_exists(
    telegram_id: int,
    first_name: str, username: str,
    referrer_telegram_id: int = None,
    balance: int = 0
) -> User | None:
    """ Создаёт юзера, если он не существует. Если юзер был создан, возвращает его. Иначе None """
    defaults = {
        'name': first_name, 'username': username, 'balance': balance,
        'referred_by_id': referrer_telegram_id, 'bot_blocked': False
    }
    user, created = await User.get_or_create(telegram_id=telegram_id, defaults=defaults)

    # Если юзер существует, а name или username не заданы, указываем
    if not created:
        user.name = first_name
        user.username = username
        user.bot_blocked = False
        await user.save()

    return user if created else None


# Read

async def get_user_or_none(telegram_id: int) -> Union[User, None]:
    return await User.get_or_none(telegram_id=telegram_id)


async def get_user_balance(telegram_id: int) -> float:
    user = await get_user_or_none(telegram_id)
    return user.balance


async def add_referral(user_telegram_id: int, referrer_id: int):
    try:
        user = await User.get(telegram_id=user_telegram_id)
        referrer = await User.get(telegram_id=referrer_id)
    except DoesNotExist:
        return

    if user.referred_by:
        return

    user.referred_by = referrer
    await user.save()


async def get_referrer_id_of_user(user_id: int):
    try:
        user = await User.get(telegram_id=user_id)
    except DoesNotExist:
        return

    return user.referred_by_id


async def get_referrals_count_by_telegram_id(user_id: int):
    try:
        user = await User.get(telegram_id=user_id)
    except DoesNotExist:
        return None

    # Если пользователь найден, то получаем количество его рефералов
    if user:
        referrals_count = await user.referrals.all().count()
        return referrals_count
    else:
        return None


async def update_last_activity(user_id: int, new_activity: datetime):
    user = await get_user_or_none(telegram_id=user_id)
    if user:
        user.last_activity = new_activity
        await user.save()


async def set_user_blocked_bot(user_id: int):
    user = await get_user_or_none(telegram_id=user_id)
    if user:
        user.bot_blocked = True
        await user.save()


async def get_all_user_ids() -> AsyncGenerator[int, None]:
    async for user_id in User.all().values_list('telegram_id', flat=True):
        yield user_id


async def get_all_users() -> list[User]:
    return await User.all()


async def get_users_online_count(minutes_threshold: int = 15) -> int:
    last_activity_threshold = datetime.utcnow() - timedelta(minutes=minutes_threshold)
    online_users_count = await User.filter(last_activity__gt=last_activity_threshold).count()
    return online_users_count


async def get_total_users_count() -> int:
    return await User.all().count()
