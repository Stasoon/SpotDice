from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardBuilder

from src.database import get_top_winners_by_count
from src.misc import MenuNavigationCallback


async def get_top_markup(stars: list, days: int = None):
    """Возвращает клавиатуру с топом игроков за конкретный период. \n
    ! stars - костыль, список из трёх строк ['', '', '⭐'],
    где одна - звёздочка, которая подставляется в выбранную кнопку"""
    top_players = await get_top_winners_by_count(days_back=days)
    builder = InlineKeyboardBuilder()
    for user in top_players:
        builder.button(
            text=f"👤 {user.name}  |  🏆 {user.wins_count}",
            url=f"tg://user?id={user.telegram_id}"
        )
    builder.adjust(1)

    nav_builder = InlineKeyboardBuilder()
    nav_builder.button(text=f'{stars[0]}За всё время',
                       callback_data=MenuNavigationCallback(branch='top_players', option='all'))
    nav_builder.button(text=f'{stars[1]}За месяц',
                       callback_data=MenuNavigationCallback(branch='top_players', option='month'))
    nav_builder.button(text=f'{stars[2]}За сутки', callback_data=MenuNavigationCallback(branch='top_players', option='day'))
    nav_builder.adjust(3)

    builder.attach(nav_builder)
    return builder.as_markup()


class UserTopPlayersKeyboards:
    @staticmethod
    async def get_day_top_players() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, отображающую топ игроков с количеством их побед за день"""
        return await get_top_markup(days=1, stars=['', '', '⭐'])

    @staticmethod
    async def get_month_top_players() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, отображающую топ игроков с количеством их побед за месяц"""
        return await get_top_markup(days=31, stars=['', '⭐', ''])

    @staticmethod
    async def get_all_time_top_players() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, отображающую топ игроков с количеством их побед за всё время"""
        return await get_top_markup(stars=['⭐', '', ''])
