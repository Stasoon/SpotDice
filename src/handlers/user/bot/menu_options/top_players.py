import asyncio

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import CallbackQuery, Message

from src.database import get_top_winners_by_count
from src.keyboards.user.top_players import get_top_players_markup
from src.messages import UserMenuMessages
from src.misc import MenuNavigationCallback


async def get_top_players_without_privacy_mode(bot: Bot, days_back: int = None):
    top_players = await get_top_winners_by_count(days_back=days_back, limit=10)

    async def get_user_info(user):
        is_private = True
        try:
            user_chat = await bot.get_chat(chat_id=user.telegram_id)
            is_private = user_chat.has_private_forwards
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            is_private = True
        return user.name, None if is_private else user.telegram_id, user.wins_count

    tasks = [get_user_info(user) for user in top_players]
    data = await asyncio.gather(*tasks)

    return data


async def handle_top_player_button(message: Message):
    top_users = await get_top_players_without_privacy_mode(bot=message.bot)

    await message.answer_photo(
        photo=UserMenuMessages.get_top_players_photo(),
        caption=UserMenuMessages.get_top_players(),
        reply_markup=get_top_players_markup(top_players=top_users, selected_period='all'),
    )


async def handle_top_players_callback(callback: CallbackQuery, callback_data: MenuNavigationCallback):
    match callback_data.option:
        case 'all': days_back = None
        case 'month': days_back = 30
        case _: days_back = 1

    top_players = await get_top_players_without_privacy_mode(bot=callback.bot, days_back=days_back)
    markup = get_top_players_markup(top_players=top_players, selected_period=callback_data.option)

    try:
        await callback.message.edit_caption(caption=UserMenuMessages.get_top_players(), reply_markup=markup)
    except TelegramBadRequest:
        pass

    await callback.answer()


def register_top_players_handlers(router: Router):
    router.message.register(handle_top_player_button, F.text.lower().contains('топ игроков'))

    router.callback_query.register(
        handle_top_players_callback,
        MenuNavigationCallback.filter((F.branch == 'top_players') & F.option)
    )
