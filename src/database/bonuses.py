import string
import random
from decimal import Decimal

from tortoise.exceptions import IntegrityError

from .models import PromoCode, BonusActivation, User


def __generate_activation_code(length=8):
    """Генерирует код активации """
    characters = f'{string.ascii_letters}{string.digits}'  # Все заглавные буквы и цифры
    code = ''.join(random.choice(characters) for _ in range(length))
    return code


# Create
async def create_bonus(amount: float, activations_count: int = 50, activation_code: str = None) -> PromoCode | None:
    """Создать новый бонус. Если activation_code не указано, будет сгенерирован рандомно."""
    amount = Decimal(amount)

    # Если активационный код не указан, генерируем рандомно
    if not activation_code:
        # Создаём новый код до тех пор, пока он будет не занят
        while True:
            code = __generate_activation_code()
            if not await is_activation_code_not_occupied(activation_code):
                activation_code = code
                break

    # Пытаемся создать бонус
    try:
        bonus = await PromoCode.create(
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
    return await PromoCode.filter(activation_code=code_to_check).exists()


async def get_bonus_by_activation_code_or_none(code: str) -> PromoCode | None:
    return await PromoCode.get_or_none(activation_code=code)


async def get_bonus_by_id_or_none(promo_code_id: int):
    return await PromoCode.get_or_none(id=promo_code_id)


async def get_active_bonuses() -> list[PromoCode]:
    return await PromoCode.filter(is_active=True).all()


# Update


async def is_user_activated_bonus(bonus, user):
    return await BonusActivation.filter(user=user, bonus=bonus).exists()


async def make_activation(bonus: PromoCode, user: User) -> bool:
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


async def deactivate_promo_code(bonus: PromoCode):
    bonus.is_active = False
    await bonus.save()
