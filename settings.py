import os
from typing import Final
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Config:
    class Bot:
        TOKEN: Final[str] = os.getenv('BOT_TOKEN', 'define me')
        OWNER_IDS: Final[tuple] = tuple(int(i) for i in str(os.getenv('BOT_OWNER_IDS')).split(','))

    class Payments:
        CRYPTO_BOT_TOKEN: Final[str] = os.getenv('CRYPTO_BOT_TOKEN')
        DEPOSITS_CHANNEL_ID: Final[int] = int(os.getenv('DEPOSITS_CHANNEL_ID'))
        WITHDRAWS_CHANNEL_ID: Final[int] = int(os.getenv('WITHDRAWS_CHANNEL_ID'))

        MAX_BET = 50_000_000.0
        winning_commission: Final[float] = 0.05

        min_withdraw_amount: Final[float] = float(300)
        min_deposit_amount: Final[float] = float(50)

    class Games:
        GAME_CHAT_ID: Final[int] = int(os.getenv('GAME_CHAT_ID'))
        EVEN_UNEVEN_CHAT_ID: Final[int] = int(os.getenv('EVEN_UNEVEN_CHAT_ID'))
        CARD_IMAGES_PATH: Final[str] = 'resources/cards'
        min_bet_amount: Final[float] = float(30)

    class Database:
        DATABASE_URL: Final[str] = os.getenv('POSTGRES_URL')
        REDIS_URL: Final[str] = os.getenv('REDIS_URL')

    class Bands:
        BAND_MEMBERS_LIMIT = 6
        maps_chat_id: int = os.getenv('BAND_MAPS_CHAT_ID')

    DEBUG: Final = bool(os.getenv('DEBUG'))
