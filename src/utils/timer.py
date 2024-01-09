import asyncio
from abc import ABC, abstractmethod

from src.database.models import Timer


class BaseTimer(ABC):

    def __init__(
            self, chat_id: int, message_id: int, seconds_expiry: int, step: int = 5,
    ):
        self.time = seconds_expiry
        self.step = step

        self.message_id = message_id
        self.chat_id = chat_id

        self.timer = None
        self.timer_id = None
        self.is_stopped = False

    async def __setup(self):
        await Timer.filter(chat_id=self.chat_id).delete()

        self.timer = await Timer.create(chat_id=self.chat_id, timer_expiry=self.time, message_id=self.message_id)
        self.timer_id = self.timer.id

    async def start(self):
        await self.__setup()

        while True:
            if not self.timer or self.is_stopped:
                return

            await asyncio.sleep(self.step)
            await self.make_tick()

            if self.timer and self.timer.timer_expiry <= 0:
                self.is_stopped = True
                break

        await self.on_time_left()

    @classmethod
    async def stop(cls, chat_id: int):
        timer = await Timer.filter(chat_id=chat_id).first()
        await Timer.filter(chat_id=chat_id).delete()
        return timer

    @abstractmethod
    async def make_tick(self):
        if self.is_stopped: return

        self.timer = await Timer.get_or_none(chat_id=self.chat_id)
        if self.timer:
            self.timer.timer_expiry -= self.step
            await self.timer.save()
        else:
            self.is_stopped = True

    @abstractmethod
    async def on_time_left(self):
        await self.timer.delete()
        self.is_stopped = True

    @staticmethod
    def format_seconds_to_time(seconds: int) -> str:
        res = []

        while seconds > 0:
            res.append(f"{seconds % 60:02}")
            seconds //= 60

        if len(res) < 2:
            res.append("00")

        return ':'.join(res[::-1])

    def __str__(self) -> str:
        if not self.timer:
            return ''

        return self.format_seconds_to_time(self.timer.timer_expiry)

