import string
import random
from decimal import Decimal

from tortoise.exceptions import IntegrityError

from .models import Bonus, BonusActivation, User


def __generate_activation_code(length=8):
    """Генерирует код активации """
    characters = f'{string.ascii_letters}{string.digits}'  # Все заглавные буквы и цифры
    code = ''.join(random.choice(characters) for _ in range(length))
    return code


# Create
async def create_bonus(amount: float, activations_count: int = 50, activation_code: str = None) -> Bonus | None:
    """Создать новый бонус. Если activation_code не указано, будет сгенерирован рандомно."""
    amount = Decimal(amount)

    # Если активационный код не указан, генерируем рандомно
    if not activation_code:
        # Создаём новый код до тех пор, пока он будет не занят
        while True:
            activation_code = __generate_activation_code()
            if await is_activation_code_not_occupied(activation_code):
                break

    # Пытаемся создать бонус
    try:
        bonus = await Bonus.create(
            amount=amount, activation_code=activation_code,
            total_activations_count=activations_count,
            remaining_activations_count=activations_count
        )
    # Если возникает ошибка уникальности, возвращаем False
    except IntegrityError:
        return None
    return bonus


# Read
async def is_activation_code_not_occupied(code_to_check) -> bool:
    return await Bonus.filter(activation_code=code_to_check).exists()


async def get_bonus_by_activation_code_or_none(code: str) -> Bonus | None:
    return await Bonus.get_or_none(activation_code=code)


async def get_active_bonuses() -> list[Bonus]:
    return await Bonus.filter(is_active=True).all()


# Update


async def is_user_activated_bonus(bonus, user):
    return await BonusActivation.filter(user=user, bonus=bonus).exists()


async def make_activation(bonus: Bonus, user: User) -> bool:
    if not bonus.is_active:
        return False

    if user.balance > 0:
        return False

    if bonus.remaining_activations_count == 0:
        bonus.is_active = False
        await bonus.save()
        return False

    bonus.remaining_activations_count -= 1
    await bonus.save()

    if not await is_user_activated_bonus(user=user, bonus=bonus):
        await BonusActivation.create(user=user, bonus=bonus)
        user.balance += bonus.amount
        await user.save()
        return True
    return False


async def deactivate_bonus(bonus: Bonus):
    bonus.is_active = False
    await bonus.save()
