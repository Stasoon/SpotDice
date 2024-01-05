import asyncio
import io
import os
import json

import aiofiles
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot
from aiogram.types import BufferedInputFile

from src.database import bands
from src.misc.enums.leagues import BandLeague


photos_file_name = 'band_maps.json'


def get_positions(league: BandLeague) -> list[tuple[int, int]]:
    match league:
        case BandLeague.GAMBLERS:
            return [(3960, 1860), (3960, 1945), (3960, 2045), (3960, 2140), (3960, 2225), (3960, 2320)]
        case BandLeague.CARD_MASTERS:
            return [(1850, 2646), (1850, 2750), (1850, 2860), (1850, 2984), (1850, 3090), (1850, 3220)]
        case BandLeague.BUSINESSMEN:
            return [(2150, 3770), (2150, 3870), (2150, 3980), (2150, 4120), (2150, 4220), (2150, 4345)]
        case BandLeague.INDUSTRIALISTS:
            return [(1900, 2580), (1900, 2690), (1900, 2800), (1900, 2920), (1900, 3030), (1900, 3160)]
        case BandLeague.MAGNATES:
            return [(1755, 2935), (1755, 3035), (1755, 3135), (1755, 3235), (1755, 3335), (1755, 3435)]
        case BandLeague.MONOPOLISTS:
            return [(3175, 1820), (3175, 1910), (3175, 2000), (3175, 2095), (3175, 2185), (3175, 2275)]


def get_map_image_path(league: BandLeague):
    folder_path = os.path.join(os.getcwd(), 'resources', 'bands')
    extension = '.png'
    image_name = ''

    match league:
        case BandLeague.GAMBLERS:
            image_name = 'gamblers'
        case BandLeague.CARD_MASTERS:
            image_name = 'card_masters'
        case BandLeague.BUSINESSMEN:
            image_name = 'businessmen'
        case BandLeague.INDUSTRIALISTS:
            image_name = 'industrialists'
        case BandLeague.MAGNATES:
            image_name = 'magnates'
        case BandLeague.MONOPOLISTS:
            image_name = 'monopolists'

    return os.path.join(folder_path, f"{image_name}{extension}")


def draw_bands_map(band_names: list[str], band_league: BandLeague) -> BufferedInputFile:
    map_img_path = get_map_image_path(band_league)
    band_names = band_names + ['Мистер Н'] * (6 - len(band_names))

    with Image.open(map_img_path) as map_image:
        bands_map = map_image

        draw = ImageDraw.Draw(bands_map)

        for band_name, position in zip(band_names, get_positions(band_league)):
            font_size = 70
            font = ImageFont.truetype("resources/fonts/font.otf", size=font_size)

            draw.text(
                xy=position, text=band_name,
                fill=(0, 0, 0),
                align='left',
                font=font
            )

        img_buffer = io.BytesIO()
        bands_map.save(img_buffer, format='PNG')

        image_bytes = img_buffer.getvalue()
        buffered_image = BufferedInputFile(image_bytes, filename=f'Карта')
        img_buffer.close()
        return buffered_image


async def run_periodic_maps_update(bot, chat_id):
    while True:
        await save_maps_photos(bot, chat_id)
        await asyncio.sleep(3600)


async def save_maps_photos(bot: Bot, chat_id: int):
    photos_data = {}
    leagues = [league for league in BandLeague if league != BandLeague.CROOKS]

    for league in leagues:
        top_league_bands = await bands.get_bands_rating_in_league(league=league, count=6)
        band_names = [band.title for band in top_league_bands]

        map_photo = draw_bands_map(band_names, league)
        map_message = await bot.send_photo(photo=map_photo, chat_id=chat_id)

        map_file_id = map_message.photo[0].file_id
        photos_data[league.value] = map_file_id

    async with aiofiles.open(photos_file_name, mode='w') as file:
        content = json.dumps(obj=photos_data, indent=4)
        await file.write(content)


async def get_bands_map_photo_file_id(league: BandLeague):
    async with aiofiles.open(photos_file_name, mode='r') as file:
        content = await file.read()
        data = json.loads(content)
        return data[str(league.value)]
