from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandObject

from src.database.transactions import deposit_to_user
from src.database import bonuses
from src.database.users import get_user_or_none
from src.messages import AdminMessages
from src.utils.text_utils import format_float_to_rub_string


# !!! При пересылке сообщения от игрока, показывать инфу о профиле
# + Командой с user_id показывать профиль

async def handle_help_command(message: Message):
    text = (
        "Балансы пользователей: \n"
        "<code>/give</code> {id} {сумма}  -  пополнить баланс \n"
        "<code>/dep</code> {id} {сумма}  -  пополнить баланс с уведомлением \n\n"
        "Промокоды: \n"
        "<code>/promo</code> {сумма} {кол-во активаций} {код}  -  создать \n"
        "<code>/promos</code>  -  посмотреть список"
    )

    await message.answer(text=text)


async def handle_give_balance_command(message: Message, command: CommandObject):
    cmd = command.command
    try:
        cmd_args = command.args.split()
        user_id = int(cmd_args[0])
        amount = float(cmd_args[1])
    except ValueError:
        await message.answer(f'Команда должна иметь формат /{cmd}'+'{id игрока} {сумма}', parse_mode='HTML')
        return

    user = await get_user_or_none(telegram_id=user_id)

    if not user:
        await message.answer('Игрок с таким user_id не найден!')
        return

    await deposit_to_user(user_id=user_id, amount=amount, create_record=True if cmd == 'dep' else False)
    await message.answer(f"Депозит начислен <a href='tg://user?id={user_id}'>игроку</a>", parse_mode='HTML')


async def handle_promo_code_command(message: Message, command: CommandObject):
    cmd_args = command.args.split()

    n = cmd_args + [None] * (3 - len(cmd_args))
    amount, activations_count, activation_code = n

    if await bonuses.is_activation_code_not_occupied(activation_code):
        await message.answer('Этот промокод уже занят!')
        return

    bonus = await bonuses.create_bonus(
        amount=amount, activations_count=activations_count, activation_code=activation_code
    )
    await message.answer(text=AdminMessages.get_bonus_description(bonus=bonus))


async def handle_promo_codes_command(message: Message):
    active_bonuses = await bonuses.get_active_bonuses()

    if not active_bonuses:
        await message.answer('Нет активных промокодов')
        return

    for bonus in active_bonuses:
        await message.answer(
            text=AdminMessages.get_bonus_description(bonus=bonus),
            reply_markup=None
        )


def register_commands_handlers(router: Router):
    router.message.register(handle_help_command, Command('help'))

    router.message.register(handle_give_balance_command, Command('give', 'dep'))

    router.message.register(handle_promo_code_command, Command('promo'))
    router.message.register(handle_promo_codes_command, Command('promos'))
