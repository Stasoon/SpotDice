from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import Command, CommandObject

from src.database.transactions import deposit_to_user
from src.database import bonuses
from src.database.users import get_user_or_none
from src.filters import ChatTypeFilter, IsAdminFilter
from src.keyboards.admin.promocodes_kbs import PromoCodesKbs
from src.messages import AdminMessages
from src.misc.callback_factories import PromoCodeCallback
from src.utils.text_utils import format_float_to_rub_string


# !!! При пересылке сообщения от игрока, показывать инфу о профиле
# + Командой с user_id показывать профиль

async def handle_help_command(message: Message):
    text = (
        "Балансы пользователей: \n"
        "<code>/give</code> {id} {сумма}  -  пополнить баланс \n"
        "<code>/dep</code> {id} {сумма}  -  пополнить баланс с уведомлением \n\n"
        "Промокоды: \n"
        "<code>/promocode</code> {сумма} {кол-во активаций} {код}  -  создать \n"
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
    if not command.args:
        await message.answer(text='Команда должна иметь формат \n<code>/promo</code> {сумма} {кол-во активаций} {код}')
        return

    cmd_args = command.args.split()
    n = cmd_args + [None] * (3 - len(cmd_args))
    amount, activations_count, activation_code = n

    if await bonuses.is_activation_code_not_occupied(activation_code):
        await message.answer('Этот промокод уже занят!')
        return

    bonus = await bonuses.create_bonus(
        amount=amount, activations_count=activations_count if activations_count else 50, activation_code=activation_code
    )
    await message.answer(text=AdminMessages.get_bonus_description(bonus=bonus))


async def handle_promo_codes_command(message: Message):
    active_promo_codes = await bonuses.get_active_bonuses()

    if not active_promo_codes:
        await message.answer('Нет активных промокодов')
        return

    for bonus in active_promo_codes:
        await message.answer(
            text=AdminMessages.get_bonus_description(bonus=bonus),
            reply_markup=PromoCodesKbs.get_deactivate_promo_code(promo_code_id=bonus.id)
        )


async def handle_deactivate_promo_code_callback(callback: CallbackQuery, callback_data: PromoCodeCallback):
    promo_code = await bonuses.get_bonus_by_id_or_none(callback_data.promo_code_id)
    await bonuses.deactivate_promo_code(bonus=promo_code)
    await callback.message.edit_text(text=f"{callback.message.text} \n\n Деактивирован")


def register_commands_handlers(router: Router):
    router.message.register(handle_help_command, Command('help'), IsAdminFilter(True), ChatTypeFilter(chat_type=ChatType.PRIVATE))

    router.message.register(handle_give_balance_command, Command('give', 'dep'), IsAdminFilter(True))

    router.message.register(handle_promo_code_command, Command('promocode'), IsAdminFilter(True))
    router.message.register(handle_promo_codes_command, Command('promos'), IsAdminFilter(True))
    router.callback_query.register(handle_deactivate_promo_code_callback, IsAdminFilter(True), PromoCodeCallback.filter(F.action == 'deactivate'))
