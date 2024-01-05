from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import Message

from src.database import users, games
from src.messages import GameErrors
from src.messages.user import UserMenuMessages, get_short_game_info_text
from src.utils.game_validations import check_rights_and_cancel_game


async def handle_profile_command(message: Message):
    user = await users.get_user_or_none(message.from_user.id)
    await message.answer(text=await UserMenuMessages.get_profile(user), parse_mode='HTML')


async def handle_my_games_command(message: Message):
    game = await games.get_user_unfinished_game(message.from_user.id)
    if not game:
        await message.answer(GameErrors.get_no_active_games(), parse_mode='HTML')
        return

    text = await get_short_game_info_text(game)

    try:
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_to_message_id=game.message_id,
            parse_mode='HTML'
        )
    except TelegramBadRequest:
        await message.answer(text, parse_mode='HTML')


async def handle_all_games_command(message: Message):
    chat_id = message.chat.id
    chat_available_games = await games.get_chat_available_games(chat_id)

    if not chat_available_games:
        await message.answer(GameErrors.get_no_active_games(), parse_mode='HTML')
        return

    for game in chat_available_games:
        text = await get_short_game_info_text(game)
        try:
            await message.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=game.message_id,
                parse_mode='HTML'
            )
        except TelegramBadRequest:
            await message.answer(text, parse_mode='HTML')


async def handle_delete_game_command(message: Message):
    # если не ответ на игру
    if not message.reply_to_message:
        return

    game = await games.get_game_by_message_id(message.reply_to_message.message_id)
    await check_rights_and_cancel_game(event=message, game=game)


def register_other_commands_handlers(router: Router):
    router.message.register(handle_delete_game_command, Command('del'))
    router.message.register(handle_profile_command, Command('profile'))
    router.message.register(handle_all_games_command, Command('allgames'))
    router.message.register(handle_my_games_command, Command('mygames'))
