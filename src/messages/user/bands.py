from decimal import Decimal

from aiogram import html

from settings import Config
from src.database.models import Band, User
from src.misc.enums.leagues import BandLeague
from src.utils.text_utils import format_float_to_rub_string, get_emoji_number


class BandsMessages:

    @staticmethod
    def get_bands_menu() -> str:
        return (
            'Мы позаботились о твоём комфорте во время игры — лови '
            '<a href="https://telegra.ph/Azartnyj-gorod-BarredLand-i-kak-tut-vsyo-ustroeno-01-08">краткую сводку</a> '
            'о том, как всё тут устроено. \n\n'
            '1⃣ В городе существует система Лиг —  ты вместе со своей Бандой поднимаешься '
            'вверх, где вас ждут ценные призы и бой с DICY \n\n'
            '2⃣ Ты можешь основать свою банду, либо примкнуть к уже существующим \n\n'
            '3⃣ Ты можешь открыть Карту Города, где отображается каждый его район и банды в нëм — '
            'Нажимай на Город -> Монополисты \n\n'
            'Один, два, три — ты уже в пути. К завоеванию титула Короля Азарта'
        )

    @staticmethod
    def get_city_description() -> str:
        return (
            '🗺 Карта города <b>BarredLand</b> \n\n'
            '❕В каждой Лиге должно быть не менее шести банд для разделения участков. '
            'Если их меньше — территорию занимает Игрок «Н»'
        )

    @staticmethod
    def get_league_map_description(league: BandLeague, band_names: list[str]):
        text = f"<b>Лига {league} и 6 Банд, занявших на ней территорию</b>"

        list_len = 6
        band_names = band_names[:list_len] + ['Мистер Н']*(list_len-len(band_names))
        enumerated_band_names = [
            f"{get_emoji_number(n)} {html.quote(band_name)}"
            for n, band_name in enumerate(band_names, start=1)
        ]
        band_names_text = "\n".join(enumerated_band_names)

        return f"{text} \n\n{band_names_text}"

    @classmethod
    def get_band_description(cls, band: Band, band_creator: User, members_scores: list[tuple[User, float | Decimal]]) -> str:
        members_text = f'🫂 Участники: ({len(members_scores)}/{Config.Bands.BAND_MEMBERS_LIMIT})'
        members_list = "\n".join(
            f"{n}) {member[0]} — {format_float_to_rub_string(member[1])}"
            for n, member in enumerate(members_scores, start=1)
        )

        return (
            f'<b>Банда "{html.quote(band.title)}"</b> \n\n'
            f'👑 Главарь: {band_creator} \n'
            f'📈 Ранг: {band.league} \n'
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
    def get_bands_menu_photo() -> str:
        return 'https://telegra.ph/file/3d5b3f9088dba0e0c39b1.png'

    @staticmethod
    def get_global_map_photo() -> str:
        return 'https://telegra.ph/file/0f6ba0c9f77dc865169a5.png'
