from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from settings import Config


bot = Bot(token=Config.Bot.TOKEN, disable_web_page_preview=True, parse_mode='HTML')

storage = MemoryStorage() if not Config.Database.REDIS_URL else RedisStorage.from_url(url=Config.Database.REDIS_URL)
dp = Dispatcher(storage=storage)
