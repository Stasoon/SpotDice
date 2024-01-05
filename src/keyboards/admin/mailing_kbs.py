from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, \
    InlineKeyboardBuilder

from .admin_keyboards import AdminKeyboardBase


class MailingKb(AdminKeyboardBase):
    @staticmethod
    def get_button_for_admin_menu():
        return KeyboardButton(text='✉ Рассылка ✉')

    @staticmethod
    def get_skip_adding_button_to_post() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Продолжить без кнопки', callback_data='continue_wout_button')
        return builder.as_markup()

    @staticmethod
    def get_cancel_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(text='🔙 Отменить', callback_data='cancel_mailing')

    @staticmethod
    def get_cancel_markup() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[MailingKb.get_cancel_button()]])

    @staticmethod
    def get_confirm_mailing() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='❗ Начать рассылку ❗', callback_data='start_mailing')
        builder.add(MailingKb.get_cancel_button())
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def generate_markup_from_text(text: str) -> InlineKeyboardMarkup:
        markup_builder = InlineKeyboardBuilder()

        lines = text.split('\n')  # Получаем строки
        for line in lines:  # итерируемся по строкам
            button_contents = line.strip().split('|')  # разделяем кнопки в строке
            row_builder = InlineKeyboardBuilder()

            for content in button_contents:
                item_parts = content.strip().split()
                text = ' '.join(item_parts[:-1])
                url = item_parts[-1]
                if text and url:
                    row_builder.button(text=text, url=url)

            row_builder.adjust(len(button_contents))
            markup_builder.attach(row_builder)

        return markup_builder.as_markup()
