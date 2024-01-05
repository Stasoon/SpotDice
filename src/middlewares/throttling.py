from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from cachetools import TTLCache

from src.messages import get_throttling_message


SECONDS_BETWEEN_ACTIONS = 0.5
cache = TTLCache(maxsize=3_000, ttl=SECONDS_BETWEEN_ACTIONS)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, only_on_spam: bool = False):
        """ Если only_on_spam = True, троттлер будет реагировать только на однотипные по содержанию сообщения """
        self.on_spam = only_on_spam

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any],
    ) -> Any:
        if self.on_spam and (hasattr(event, 'text') and event.text) or (hasattr(event, 'data') and event.data):
            event_key = event.text[:8] if isinstance(event, Message) and event.text else str(event.data)[:8]
        else:
            event_key = 'msg' if isinstance(event, Message) else 'callb'

        user_id = event.from_user.id
        key = hash(event_key) + user_id
        message_count = cache.get(key, 0) + 1
        cache[key] = message_count

        if message_count == 2:
            await event.answer(get_throttling_message())
            return
        elif message_count > 2:
            return

        await handler(event, data)
