from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.database.users import get_user_or_none


class UserExistFilter(BaseFilter):
    def __init__(self, user_should_exist: bool = True):
        self.user_should_exist = user_should_exist

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id
        user = await get_user_or_none(user_id)
        return bool(user) is self.user_should_exist
