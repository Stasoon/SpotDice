from src.database import bands
from src.database.models import Band
from src.misc.enums.leagues import BandLeague
from src import bot


async def send_league_updated(band: Band, *args, **kwargs):
    text = f'🎉 Поздравляю! твоя банда перешла в лигу {band.league}!'

    match band.league:
        # case BandLeague.GAMBLERS:
        #     text = (
        #         'DICY: Ну что, а теперь запомни, ты теперь картежник, ты теперь с улицей, а кругом враги. \n'
        #         'Твоя банда набрала ... выигрышей и перешла в <b>лигу Картежников</b>. \n'
        #         '🎉 Добро пожаловать!'
        #     )
        case BandLeague.CARD_MASTERS:
            text = (
                'DICY: Вижу, ты начинаешь осваиваться в этом городе. Сколько джекпотов сорвал? \n'
                'Впрочем, неважно. Всё равно все твои деньги станут моими. \n'
                '🎉 Добро пожаловать в Лигу <b>Мастеров Карт</b>!'
            )
        case BandLeague.BUSINESSMEN:
            text = (
                'DICY: Кубики бросаются, ставки мутятся! \n'
                'Интересно, как далеко ты зайдёшь. Может, и в историю города войдешь... \n'
                '🎉 Добро пожаловать в Лигу <b>Бизнесменов</b>!'
            )
        case BandLeague.INDUSTRIALISTS:
            text = (
                'DICY: Вижу, что ты настроен серьезно. \n'
                'Учти, что с большими победами приходят и большие поражения. \n'
                'Так что не воспринимай их близко к сердцу. \n'
                '🎉 Ну а пока веселись, ведь ты перешел в Лигу <b>Промышленников</b>!'
            )

    for member in await bands.get_band_members(band_id=band.id):
        await bot.send_message(chat_id=member.telegram_id, text=text)
