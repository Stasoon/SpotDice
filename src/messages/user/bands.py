import html
from decimal import Decimal

from settings import Config
from src.database.models import Band, User
from src.misc.enums.leagues import BandLeague
from src.utils.text_utils import format_float_to_rub_string


def get_member_link(member: User):
    if member.telegram_id:
        return f"<a href='tg://user?id={member.telegram_id}'>{html.escape(member.name)}</a>"
    else:
        return html.escape(member.name)


class BandsMessages:

    @staticmethod
    def get_bands_menu() -> str:
        return 'Меню банд'

    @staticmethod
    def get_league_name(league: BandLeague) -> str:
        match league:
            case BandLeague.CROOKS:
                return 'Жулики'
            case BandLeague.GAMBLERS:
                return 'Картёжники'
            case BandLeague.CARD_MASTERS:
                return 'Мастера карт'
            case BandLeague.BUSINESSMEN:
                return 'Бизнесмены'
            case BandLeague.INDUSTRIALISTS:
                return 'Промышленники'
            case BandLeague.MAGNATES:
                return 'Магнаты'
            case BandLeague.MONOPOLISTS:
                return 'Монополисты'

    @classmethod
    def get_band_description(cls, band: Band, band_creator: User, members_scores: list[tuple[User, float | Decimal]]) -> str:
        members_text = f'🫂 Участники: ({len(members_scores)}/{Config.Bands.BAND_MEMBERS_LIMIT})'
        members_list = "\n".join(
            f"{n}) {member[0]} — {format_float_to_rub_string(member[1])}"
            for n, member in enumerate(members_scores, start=1)
        )

        return (
            f'<b>Банда "{band.title}"</b> \n\n'
            f'👑 Главарь: {band_creator} \n'
            f'📈 Ранг: {cls.get_league_name(band.league)} \n'
            f'💰 Общак: {format_float_to_rub_string(band.score)} \n\n'
            f'{members_text} \n{members_list}'
        )

    @classmethod
    def get_ask_for_join_band(cls, band: Band, band_creator: User, members_scores) -> str:
        band_description = cls.get_band_description(band=band, band_creator=band_creator, members_scores=members_scores)
        return f'Хотите ли вы вступить в эту банду? \n\n{band_description}'

    @staticmethod
    def ask_for_member_to_kick() -> str:
        return 'Нажмите на пользователя, которого хотите исключить:'

    @staticmethod
    def get_global_map_photo() -> str:
        return 'https://telegra.ph/file/0f6ba0c9f77dc865169a5.png'

    @staticmethod
    def get_leagues_rules_explanation() -> str:
        return (
            'Не имея Банды – игрок имеет ранг «Жулик» \n\n'
            'После создания или вступления в Банду, игрок вступает в систему лиг - читай '
            'подробнее в нашей <a href="https://telegra.ph/Pravila-lig-01-04">новостной сводке</a>.'
        )

    @staticmethod
    def get_rewards_explanation() -> str:
        return (
            'Чем выше находится Банда, тем более ценные призы получит каждый ее член в конце сезона. \n\n'
            'Призы будут выдаваться как внутри игры, так и высылаться каждому члену Банды по почте в вещественном виде. \n\n'
            'Совсем скоро в <a href="https://t.me/barrednews">запрещённых новостях</a> города BarredLand мы представим вам общий список возможных наград. \n\n'
            'Ожидай с нетерпением!'
        )

    @staticmethod
    def get_bands_rules_explanation() -> str:
        return (
            '<b>BarredLand</b> наконец-то открыл свои двери для всех претендентов на звание <b>КОРОЛЯ азарта</b>! \n\n'
            'Прояви свои лучшие качества в поиске верных союзников и вместе с ними сражайся за место в Городе! \n'
            'Читай как работают банды в нашей <a href="https://telegra.ph/Kak-zhe-rabotayut-Bandy-01-04">новостной сводке</a>.'
        )

    @staticmethod
    def get_city_rules_explanation() -> str:
        return (
            'Всё что сейчас происходит, тесно связано с двумя местами – заведением @SpotDice и Городом BarredLand! \n\n'
            'Создав или вступив в Банду, игрок автоматически становится частью города, однако начинать придется с самых низов. \n'
            'Только лучшие получат место на вершине! \n\n'
            'О том, как устроен город - читай в нашей <a href="https://telegra.ph/Pravila-Goroda-01-04">новостной сводке</a>.'
        )
