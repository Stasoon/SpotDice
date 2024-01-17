from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.messages import UserMenuMessages
from src.keyboards.user import UserMenuKeyboards


async def handle_events_button(message: Message):
    await message.answer(text='Бот обновился!', reply_markup=UserMenuKeyboards.get_main_menu())


# async def handle_back_to_events_callback(callback: CallbackQuery):
#     await callback.message.edit_text(text=UserMenuMessages.get_events(), reply_markup=UserMenuKeyboards.get_events())
#
#
# async def handle_spot_dice_plans_callback(callback: CallbackQuery):
#     await callback.message.edit_text(
#         text='SpotDice стремится подарить каждому из игроков незабываемый опыт от игры \n\n'
#              'Для этого мы ежедневно расширяем и развиваем возможности в нашем заведении. \n'
#              'Смотри наши планы в <a href="https://telegra.ph/Plany-SpotDice-01-06">новостной сводке</a>.',
#         reply_markup=UserMenuKeyboards.get_back_to_events()
#     )


def register_events_handlers(router: Router):
    router.message.register(handle_events_button, F.text.lower().contains('события'))
    # router.callback_query.register(handle_back_to_events_callback, MenuNavigationCallback.filter(F.branch=='events'))
    # router.callback_query.register(handle_spot_dice_plans_callback, F.data == 'spotdice_plans')
