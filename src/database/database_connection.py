from tortoise import Tortoise

from src.utils.logging import logger


async def start_database(db_url: str):
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["src.database.models"]},
    )

    try:
        await Tortoise.generate_schemas()
    except Exception as e:
        logger.error(f'Ошибка при подключении к БД: {e}')


async def stop_database():
    await Tortoise.close_connections()

