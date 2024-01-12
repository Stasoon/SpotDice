from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import (
    InlineKeyboardMarkup, KeyboardButton,
    ReplyKeyboardMarkup, InlineKeyboardBuilder
)


from src.misc import MenuNavigationCallback


invite_link = 'tg://msg_url?url=https://t.me/{bot_username}?start=ref{user_tg_id}' \
              '&text=Присоединяйся%20по%20моей%20ссылке'

agreement_url = 'https://teletype.in/@spotdice/WEIwyj5vu3i'


class UserMenuKeyboards:

    @staticmethod
    def get_user_agreement() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='📃 Соглашение', web_app=WebAppInfo(url=agreement_url))
        return builder.as_markup()

    @staticmethod
    def get_user_agreement_with_need_sub(url: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='📃 Соглашение', web_app=WebAppInfo(url=agreement_url),)
        builder.button(text='Канал', url=url)
        builder.button(text='✅ Проверить', callback_data='check_subscribe')
        builder.adjust(1)
        return builder.as_markup()

    # branch MAIN
    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        menu_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎰  Играть  🎰")],
                [KeyboardButton(text="🎩 Профиль"), KeyboardButton(text="🕸️ Банды")],
                [KeyboardButton(text="🏆 Топ игроков"), KeyboardButton(text="ℹ Информация")],
            ],
            resize_keyboard=True, input_field_placeholder=None
        )
        return menu_kb

    # Events
    @staticmethod
    def get_events():
        builder = InlineKeyboardBuilder()

        builder.button(text='🃏 битва Игрока «Н» с DICY', url='https://t.me/barrednews/31')
        builder.button(text='▫ Планы SpotDice', callback_data='spotdice_plans')

        return builder.adjust(1).as_markup()

    @staticmethod
    def get_back_to_events():
        builder = InlineKeyboardBuilder()
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='events'))
        builder.adjust(1)
        return builder.as_markup()

    # branch PROFILE
    @staticmethod
    def get_profile() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, которая должна отображаться после перехода в Профиль"""
        builder = InlineKeyboardBuilder()

        builder.button(text='💳 Пополнить', callback_data=MenuNavigationCallback(branch='profile', option='deposit'))
        builder.button(text='💰 Вывести', callback_data=MenuNavigationCallback(branch='profile', option='withdraw'))
        builder.button(
            text='🎁 Активировать бонус',
            callback_data=MenuNavigationCallback(branch='profile', option='bonus')
        )
        builder.button(
            text='👥 Реферальная система',
            callback_data=MenuNavigationCallback(branch='profile', option='referral_system')
        )

        builder.adjust(2, 1)
        return builder.as_markup()

    @staticmethod
    def get_cancel_reply() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True,
            is_persistent=True
        )

    @staticmethod
    def get_referral_system(bot_username: str, user_telegram_id: int) -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, которая должна отображаться при переходе в Реферальную систему"""
        builder = InlineKeyboardBuilder()

        url = invite_link.format(bot_username=bot_username, user_tg_id=user_telegram_id)
        builder.button(text='📲 Пригласить друга', url=url)
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='profile'))
        builder.adjust(1)

        return builder.as_markup()

    # branch INFORMATION
    @staticmethod
    def get_information() -> InlineKeyboardMarkup:
        """Возвращает клавиатуру, которая должна отображаться при переходе во вкладку Информация"""
        builder = InlineKeyboardBuilder()

        builder.button(text='♦ Канал', url='https://t.me/barrednews')
        builder.button(text='🪙 Выплаты', url='https://t.me/spotdiceV')
        builder.button(text='⭐ ЧАТ', url='https://t.me/SpotDice')
        builder.button(text='📃 Соглашение', web_app=WebAppInfo(url='https://telegra.ph/Polzovatelskoe-soglashenie-01-07'))

        builder.adjust(2, 1, 1)
        return builder.as_markup()



