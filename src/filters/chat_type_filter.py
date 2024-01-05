from typing import Union, List

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.enums.chat_type import ChatType


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, List[str], List[ChatType]] = ChatType.PRIVATE):
        self.chat_type = chat_type

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        message = event if isinstance(event, Message) else event.message

        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
