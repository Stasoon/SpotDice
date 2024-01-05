from aiogram.filters import BaseFilter
from aiogram.types import Message


class MessageIsCommand(BaseFilter):
    def __init__(self, should_be_command: bool = True):
        self.should_be_command = should_be_command

    async def __call__(self, message: Message, *args, **kwargs) -> bool:
        flag = message.text and message.text.startswith('/')
        return flag is self.should_be_command

