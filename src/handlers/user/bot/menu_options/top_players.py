from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from src.keyboards import UserTopPlayersKeyboards
from src.messages import UserMenuMessages
from src.misc import MenuNavigationCallback


async def handle_top_player_button(message: Message):
    await message.answer(
        text=UserMenuMessages.get_top_players(),
        reply_markup=await UserTopPlayersKeyboards.get_all_time_top_players(),
        parse_mode='HTML'
    )


async def handle_top_players_callback(callback: CallbackQuery, callback_data: MenuNavigationCallback):
    # костыли, но выглядит красиво
    markup = None
    if callback_data.option == 'all':
        markup = await UserTopPlayersKeyboards.get_all_time_top_players()
    elif callback_data.option == 'month':
        markup = await UserTopPlayersKeyboards.get_month_top_players()
    elif callback_data.option == 'day':
        markup = await UserTopPlayersKeyboards.get_day_top_players()

    try:
        await callback.message.edit_text(
            text=UserMenuMessages.get_top_players(),
            reply_markup=markup,
            parse_mode='HTML'
        )
    except TelegramBadRequest:
        pass

    await callback.answer()


def register_top_players_handlers(router: Router):
    router.message.register(handle_top_player_button, F.text.lower().contains('топ игроков'))

    router.callback_query.register(handle_top_players_callback, MenuNavigationCallback.filter(
        (F.branch == 'top_players') & F.option))
