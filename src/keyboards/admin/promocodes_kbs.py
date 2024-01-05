from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.misc.callback_factories import PromoCodeCallback


class PromoCodesKbs:
    @staticmethod
    def get_deactivate_promo_code(promo_code_id: int):
        builder = InlineKeyboardBuilder()
        builder.button(
            text='❌ Отменить',
            callback_data=PromoCodeCallback(promo_code_id=promo_code_id, action='deactivate')
        )
        return builder.as_markup()
