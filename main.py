import asyncio

from src import start_bot
from src.utils import setup_logger


async def main():
    setup_logger()
    await start_bot()


if __name__ == '__main__':
    asyncio.run(main=main())
