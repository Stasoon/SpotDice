from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.handlers.user.bot import even_uneven
from src.handlers.user.bot.menu_options.bands import show_band_to_join
from src.messages import get_full_game_info_text, GameErrors
from src.keyboards import UserPrivateGameKeyboards
from src.keyboards.user import UserMenuKeyboards
from src.messages.user import UserMenuMessages
from src.database import users, games, referral_links
from src.misc import GameStatus


# region Utils


async def send_welcome(start_message: Message):
    await start_message.answer_sticker(
        # text=UserMenuMessages.get_welcome(start_message.from_user.first_name),
        sticker=UserMenuMessages.get_welcome_sticker(),
        reply_markup=UserMenuKeyboards.get_main_menu(),
        parse_mode='HTML'
    )


async def send_user_agreement(to_message: Message):
    await to_message.answer_animation(
        animation=UserMenuMessages.get_user_agreement_animation(),
        reply_markup=UserMenuKeyboards.get_user_agreement()
    )


async def create_user(telegram_user):
    # создаём пользователя, если не существует
    created_user = await users.create_user_if_not_exists(
        first_name=telegram_user.first_name, username=telegram_user.username, telegram_id=telegram_user.id
    )
    return created_user


async def process_referral_code_arg(command_args: str, new_user_id: int) -> bool:
    """Обрабатывает реферальный код. Если код невалидный, возвращает False. """
    args = command_args.split()
    if not args[0].isdigit():
        return False

    referral_code = int(args[0])
    return await users.add_referral(referrer_id=referral_code, user_telegram_id=new_user_id)


# endregion


async def handle_start_cmd_with_user_referral_link(message: Message, command: CommandObject):
    created_user = await create_user(message.from_user)
    await send_welcome(message)

    # если пользователь зашёл впервые - обрабатываем реферальную ссылку
    command_args = command.args.replace('ref', '')
    if created_user:
        await send_user_agreement(to_message=message)
        await process_referral_code_arg(command_args, message.from_user.id)


async def handle_empty_start_cmd(message: Message):
    # создаём пользователя, если не существует
    created_user = await create_user(message.from_user)
    # отправляем приветствие
    await send_welcome(message)

    if created_user:
        await send_user_agreement(to_message=message)


async def handle_promotion_link_start_cmd(message: Message, command: CommandObject):
    created_user = await create_user(message.from_user)
    await send_welcome(message)

    if created_user:
        await referral_links.increase_users_count(name=command.args)
        await send_user_agreement(to_message=message)


async def handle_start_to_show_game_cmd(message: Message, command: CommandObject):
    await create_user(message.from_user)
    game_number = int(command.args.split('_')[2])
    game = await games.get_game_obj(game_number)

    if not game or game.status != GameStatus.WAIT_FOR_PLAYERS:
        await message.answer(text=GameErrors.get_game_is_finished(), reply_markup=UserMenuKeyboards.get_main_menu())
        return

    await message.answer(
        text=await get_full_game_info_text(game),
        reply_markup=await UserPrivateGameKeyboards.show_game(game),
        parse_mode='HTML'
    )


async def handle_even_u_neven_cmd(message: Message, command: CommandObject, state: FSMContext):
    # такой формат аргументов задаётся в коде игры
    await create_user(message.from_user)
    round_num, bet_option = command.args.replace('EuN_', '', 1).split('_')
    await even_uneven.show_bet_entering(message=message, state=state, round_number=round_num, bet_option=bet_option)


async def handle_join_band(message: Message, command: CommandObject):
    await create_user(message.from_user)
    band_id = int(command.args.replace('joinband', ''))
    await show_band_to_join(bot=message.bot, user_id=message.from_user.id, band_id=band_id)


# endregion


def register_start_command_handler(router: Router):
    # Ставка из EvenUneven
    router.message.register(handle_even_u_neven_cmd, CommandStart(deep_link=True, magic=F.args.startswith('EuN_')))

    # Присоединение к игре из чата
    router.message.register(handle_start_to_show_game_cmd, CommandStart(deep_link=True, magic=F.args.startswith('_')))

    # Присоединение к банде
    router.message.register(handle_join_band, CommandStart(deep_link=True, magic=F.args.startswith('joinband')))

    # Запуск бота по реферальной ссылке игрока
    router.message.register(
        handle_start_cmd_with_user_referral_link, CommandStart(deep_link=True, magic=F.args.startswith('ref'))
    )

    # Команда /start с рекламной ссылкой
    router.message.register(handle_promotion_link_start_cmd, CommandStart(deep_link=True))

    # Пустая команда /start
    router.message.register(handle_empty_start_cmd, CommandStart(deep_link=False))


