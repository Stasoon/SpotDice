from aiogram.filters import BaseFilter
from aiogram.types import Message


class GameChatFilter(BaseFilter):
    def __init__(self, game_chat_username: str):
        self.target_username = game_chat_username

    async def __call__(self, message: Message) -> bool:
        return message.chat.username == self.target_username
