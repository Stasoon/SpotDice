from aiogram.types import KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.keyboards.admin.admin_keyboards import AdminKeyboardBase
from src.database.models import ReferralLink
from src.misc.callback_factories import ReferralLinkCallback


class ReferralLinksKb(AdminKeyboardBase):
    @staticmethod
    def get_button_for_admin_menu() -> KeyboardButton:
        return KeyboardButton(text='🔗 Реферальные ссылки 🔗')

    @staticmethod
    def get_cancel() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Отменить', callback_data=ReferralLinkCallback(action='cancel'))
        return builder.as_markup()

    @staticmethod
    def get_referral_links_actions() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='➕ Добавить ссылку', callback_data=ReferralLinkCallback(action='add'))
        builder.button(text='➖ Удалить ссылку', callback_data=ReferralLinkCallback(action='delete'))
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def get_links_to_delete(links: list[ReferralLink]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for n, link in enumerate(links, start=1):
            builder.button(
                text=f"❌ {n}) {link.name} : 👥 {link.user_count}",
                callback_data=ReferralLinkCallback(action='delete', link_id=link.id)
            )

        builder.button(text='Отменить', callback_data=ReferralLinkCallback(action='cancel'))
        builder.adjust(1)
        return builder.as_markup()
