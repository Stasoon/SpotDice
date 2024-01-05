from aiogram.utils.keyboard import KeyboardButton, InlineKeyboardBuilder, InlineKeyboardMarkup

from .admin_keyboards import AdminKeyboardBase


class StatisticsKbs(AdminKeyboardBase):
    @staticmethod
    def get_button_for_admin_menu() -> KeyboardButton:
        return KeyboardButton(text='📊 Статистика 📊')

    @staticmethod
    def get_() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='За день')
        builder.button(text='За неделю')
        builder.button(text='За месяц')
        builder.button(text='За всё время')

        builder.adjust(2)
        return builder.as_markup()
