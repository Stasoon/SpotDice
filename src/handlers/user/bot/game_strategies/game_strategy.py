from abc import ABC, abstractmethod

from aiogram import Router, Bot

from src.database import Game


class GameStrategy(ABC):

    @staticmethod
    @abstractmethod
    async def start_game(bot: Bot, game: Game):
        ...

    @staticmethod
    @abstractmethod
    async def finish_game(bot: Bot, game: Game):
        ...

    @classmethod
    @abstractmethod
    def register_moves_handlers(cls, router: Router):
        ...
