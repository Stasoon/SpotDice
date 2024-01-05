from aiogram.types import KeyboardButton

from src.keyboards.admin.admin_keyboards import AdminKeyboardBase


class ExportKb(AdminKeyboardBase):
    @staticmethod
    def get_button_for_admin_menu():
        return KeyboardButton(text='📤 Экспорт данных 📤')
