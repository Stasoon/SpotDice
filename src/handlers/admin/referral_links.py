from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.keyboards.admin import ReferralLinksKb
from src.messages import AdminMessages
from src.database import referral_links
from src.misc import AdminStates
from src.misc.callback_factories import ReferralLinkCallback


async def handle_referral_links_button(message: Message):
    links = await referral_links.get_all_links()
    bot_username = (await message.bot.get_me()).username

    text = AdminMessages.get_referral_links_list(bot_username=bot_username, referral_links=links)
    await message.answer(text=text, reply_markup=ReferralLinksKb.get_referral_links_actions())


async def handle_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await handle_referral_links_button(message=callback.message)
    await callback.message.delete()
    await state.clear()


async def handle_add_referral_link_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='🔘 Введите название. Можно использовать цифры и английские буквы:',
        reply_markup=ReferralLinksKb.get_cancel()
    )
    await state.set_state(AdminStates.ReferralLinksAdding.wait_for_name)


async def handle_referral_link_name(message: Message, state: FSMContext):
    error_text = None
    if not message.text.isascii():
        error_text = '❗В сообщении есть русские буквы. Попробуйте снова:'
    elif not message.text.isalnum():
        error_text = '❗В сообщении есть символы. Попробуйте снова:'
    elif await referral_links.is_link_exists(message.text):
        error_text = '❗Такая ссылка уже существует. Попробуйте снова:'

    if error_text:
        await message.answer(text=error_text, reply_markup=ReferralLinksKb.get_cancel())
        return

    await referral_links.create_referral_link(name=message.text)
    await message.answer(text='Ссылка создана')
    await handle_referral_links_button(message=message)
    await state.clear()


async def handle_delete_referral_link_callback(callback: CallbackQuery):
    links = await referral_links.get_all_links()

    await callback.message.edit_text(
        text='🔘 Нажмите на ссылку, которую хотите удалить:',
        reply_markup=ReferralLinksKb.get_links_to_delete(links)
    )


async def handle_link_to_delete(callback: CallbackQuery, callback_data: ReferralLinkCallback):
    await referral_links.delete_link(link_id=callback_data.link_id)
    await handle_delete_referral_link_callback(callback=callback)


def register_referral_links_handlers(router: Router):
    router.callback_query.register(handle_cancel_callback, ReferralLinkCallback.filter(F.action == 'cancel'))
    router.message.register(handle_referral_links_button, F.text.lower().contains('реферальные ссылки'))

    router.callback_query.register(
        handle_add_referral_link_callback, ReferralLinkCallback.filter((F.action == 'add') & (~F.link_id))
    )
    router.message.register(handle_referral_link_name, AdminStates.ReferralLinksAdding.wait_for_name)

    router.callback_query.register(
        handle_delete_referral_link_callback, ReferralLinkCallback.filter((F.action == 'delete') & (~F.link_id))
    )
    router.callback_query.register(handle_link_to_delete, ReferralLinkCallback.filter(F.action == 'delete'))
