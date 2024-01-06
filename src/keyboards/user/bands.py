from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup

from src.database.models import Band, User
from src.misc.callback_factories import BandCallback, BandMemberCallback, MenuNavigationCallback, BandsMapCallback
from src.misc.enums.leagues import BandLeague


def number_to_emoji(number: int) -> str:
    emoji_digits = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
    return ''.join(emoji_digits[int(d)] for d in str(number))


class BandsKeyboards:
    @staticmethod
    def get_bands_menu(user_band: Band = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='ℹ Информация', callback_data=MenuNavigationCallback(branch='bands', option='info'))
        builder.button(text='🏙 Город', callback_data=MenuNavigationCallback(branch='bands', option='city'))
        if not user_band:
            builder.button(
                text='➕ Создать свою банду', callback_data=MenuNavigationCallback(branch='bands', option='create')
            )
        else:
            builder.button(text=f"Ваша банда: {user_band.title}", callback_data=BandCallback(band_id=user_band.id))
        builder.button(text='📊 Рейтинг', callback_data=MenuNavigationCallback(branch='bands', option='rating'))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_back_to_bands_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='🔙 Отменить', callback_data=MenuNavigationCallback(branch='bands', option=None))
        return builder.as_markup()

    @staticmethod
    def get_band_member_actions(band_id: int):
        builder = InlineKeyboardBuilder()
        builder.button(text='🚶‍♂ Покинуть банду', callback_data=BandCallback(band_id=band_id, action='leave'))
        builder.button(text='👿 Конкуренты', callback_data=BandCallback(band_id=band_id, action='competitors'))
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='bands', option=None))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_creator_band_actions(bot_username: str, band_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        invite_link = 'tg://msg_url?url=https://t.me/{bot_username}?' \
                      'start=joinband{band_id}&text=%0AПриглашаю%20тебя%20в%20банду!'

        builder.button(text='🔗 Пригласить участника', url=invite_link.format(bot_username=bot_username, band_id=band_id))
        builder.button(text='✏ Изменить название', callback_data=BandCallback(band_id=band_id, action='rename'))
        builder.button(text='🚶‍♂ Исключить участника', callback_data=BandCallback(band_id=band_id, action='kick'))
        builder.button(text='❌ Распустить банду', callback_data=BandCallback(band_id=band_id, action='delete'))
        builder.button(text='👿 Конкуренты', callback_data=BandCallback(band_id=band_id, action='competitors'))
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='bands', option=None))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_kick_members(band_id: int, members: list[User]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for member in members:
            builder.button(
                text=f"❌ {member.name}",
                callback_data=BandMemberCallback(band_id=band_id, user_id=member.telegram_id, action='kick')
            )
        builder.button(text='🔙 Назад', callback_data=BandCallback(band_id=band_id))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_consider_delete_band(band_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Наверное, нет', callback_data=BandCallback(band_id=band_id))
        builder.button(text='УДАЛИТЬ', callback_data=BandCallback(band_id=band_id, action='final_delete'))
        builder.button(text='Нееееет!!!', callback_data=BandCallback(band_id=band_id))
        builder.button(text='Пожалуй, не буду', callback_data=BandCallback(band_id=band_id))
        builder.button(text='🔙 Одуматься', callback_data=BandCallback(band_id=band_id))
        builder.adjust(2, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_join_band(band_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Присоединиться', callback_data=BandCallback(band_id=band_id, action='join'))
        return builder.as_markup()

    @staticmethod
    def get_band_competitors(user_band: Band, bands: list[Band]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for band in bands:
            star_text = "✴ " if band == user_band else ""
            builder.button(
                text=f"{star_text}{band.title} - 💰 {float(band.score)}",
                url=str(band.creator.get_mention_url())
            )
        builder.button(text="🔙 Назад", callback_data=BandCallback(band_id=user_band.id))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_global_rating(bands: list[Band], user_band: Band = None, user_band_ranking: int = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for n, band in enumerate(bands, start=1):
            creator_link = band.creator.get_mention_url()
            builder.button(text=f"{number_to_emoji(n)} {band.title} - {band.league}", url=creator_link)

        if user_band and user_band_ranking and len(bands) < user_band_ranking:
            builder.button(text='...', callback_data='*')
            text = f"{number_to_emoji(user_band_ranking)} {user_band.title} - {user_band.league}"
            builder.button(text=text, url=user_band.creator.get_mention_url())

        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='bands', option=None))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_city(current_league: BandLeague = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for league in BandLeague:
            if league != BandLeague.CROOKS:
                text = f"{'🔘' if league == current_league else ''} {league}"
                builder.button(text=text, callback_data=BandsMapCallback(league=league, current_league=current_league))

        builder.adjust(2)
        navigation_builder = InlineKeyboardBuilder()
        if current_league is None:
            navigation_builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='bands', option=None))
        else:
            navigation_builder.button(text='🔙 На общую карту', callback_data=MenuNavigationCallback(branch='bands', option='city'))
        return builder.attach(navigation_builder).as_markup()

    @staticmethod
    def get_info() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Правила лиг', callback_data=MenuNavigationCallback(branch='bands', option='leagues_rules'))
        builder.button(text='Призы', callback_data=MenuNavigationCallback(branch='bands', option='rewards'))
        builder.button(text='Как работают банды?', callback_data=MenuNavigationCallback(branch='bands', option='bands_rules'))
        builder.button(text='Правила Города', callback_data=MenuNavigationCallback(branch='bands', option='city_rules'))
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='bands', option=None))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_back_to_info() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='🔙 Назад', callback_data=MenuNavigationCallback(branch='bands', option='info'))
        builder.adjust(1)
        return builder.as_markup()
