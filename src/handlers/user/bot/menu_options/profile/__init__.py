from src.database import users
from src.keyboards import UserMenuKeyboards
from src.messages import UserMenuMessages
from .profile import register_profile_handlers


async def get_profile_message_data(user_id: int) -> dict:
    user = await users.get_user_or_none(user_id)
    text = await UserMenuMessages.get_profile(user)
    reply_markup = UserMenuKeyboards.get_profile()
    return {'text': text, 'reply_markup': reply_markup, 'parse_mode': 'HTML'}
