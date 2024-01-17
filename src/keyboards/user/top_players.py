from typing import Literal

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder

from src.misc import MenuNavigationCallback


def __get_nav_builder(selected_period: Literal['all', 'day', 'month']) -> InlineKeyboardBuilder:
    nav_builder = InlineKeyboardBuilder()

    match selected_period:
        case 'all': stars = ['⭐', '', '']
        case 'month': stars = ['', '⭐', '']
        case _: stars = ['', '', '⭐']

    nav_builder.button(
        text=f'{stars[0]}За всё время', callback_data=MenuNavigationCallback(branch='top_players', option='all'))
    nav_builder.button(
        text=f'{stars[1]}За месяц', callback_data=MenuNavigationCallback(branch='top_players', option='month'))
    nav_builder.button(
        text=f'{stars[2]}За сутки', callback_data=MenuNavigationCallback(branch='top_players', option='day'))
    nav_builder.adjust(3)

    return nav_builder


def get_top_players_markup(
        top_players: list[tuple[str, int | None, int]], selected_period: Literal['all', 'day', 'month']
) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру, отображающую топ игроков с количеством их побед.
    :param top_players: Список кортежей (имя, telegram id, количество побед).
    :param selected_period: За какой период отобразить.
    """
    builder = InlineKeyboardBuilder()

    for user_data in top_players:
        name, telegram_id, wins_count = user_data
        text = f"👤 {name}  |  🏆 {wins_count}"

        if telegram_id:
            builder.button(text=text, url=f"tg://user?id={telegram_id}")
        else:
            builder.button(text=text, callback_data='*')

    builder.adjust(1)
    nav_builder = __get_nav_builder(selected_period=selected_period)
    return builder.attach(nav_builder).as_markup()
