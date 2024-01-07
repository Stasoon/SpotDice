from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from settings import Config
from src import bot
from src.database import bands
from src.keyboards.user.bands import BandsKeyboards
from src.messages.user.bands import BandsMessages
from src.misc import MenuNavigationCallback
from src.misc.callback_factories import BandCallback, BandMemberCallback, BandsMapCallback
from src.misc.states import BandCreationStates, BandEditStates
from src.utils.draw_bands_map import get_bands_map_photo_file_id


# region Utils


async def get_title_or_send_error(title_message: Message) -> str | None:
    # Убираем лишние пробелы
    band_title = ' '.join(part for part in title_message.text.strip().split(' ') if part != '')
    max_title_len = 20

    if len(band_title) > max_title_len:
        await title_message.answer(f'Название банды может иметь максимальную длину в {max_title_len} символов.'
                                   f'Попробуйте ещё раз:')
        return None

    if band_title.isdigit():
        await title_message.answer('Название банды должно содержать хотя бы одну букву! \nПопробуйте ещё раз:')
        return None

    if not band_title.replace(' ', '').isalnum():
        await title_message.answer(
            text='Название банды может содержать только русские и английские буквы, пробелы, а также числа. \n'
                 'Попробуйте ещё раз:'
        )
        return None

    if await bands.is_band_title_taken(title=band_title):
        await title_message.answer('Это название уже занято! Попробуйте ещё раз:')
        return None

    return band_title


async def __get_bands_menu_message_data(for_user_id: int) -> dict:
    user_band = await bands.get_user_band(telegram_id=for_user_id)

    text = BandsMessages.get_bands_menu()
    markup = BandsKeyboards.get_bands_menu(user_band=user_band)

    return {'text': text, 'reply_markup': markup}


async def __get_user_band_message_data(band_id: int, user_id: int) -> dict:
    band = await bands.get_band_by_id(band_id=band_id)
    if not band:
        return await __get_bands_menu_message_data(for_user_id=user_id)

    band_members = await bands.get_sorted_band_members_with_scores(band_id=band_id)

    text = BandsMessages.get_band_description(band=band, band_creator=band.creator, members_scores=band_members)
    if band.creator.telegram_id == user_id:
        bot_username = (await bot.get_me()).username
        markup = BandsKeyboards.get_creator_band_actions(band_id=band_id, bot_username=bot_username)
    else:
        markup = BandsKeyboards.get_band_member_actions(band_id=band_id)
    return {'text': text, 'reply_markup': markup}


async def show_band_to_join(bot: Bot, user_id: int, band_id: int):
    band = await bands.get_band_by_id(band_id=band_id)
    if not band:
        await bot.send_message(chat_id=user_id, text='Банда была удалена!')
        return

    # Если уже является участником, показываем банду вместо предложения вступить
    user_band = await bands.get_user_band(telegram_id=user_id)
    if user_band:
        await bot.send_message(chat_id=user_id, text=f'Вы уже являетесь участником банды {user_band.title}')
        band_message = await __get_user_band_message_data(band_id=user_band.id, user_id=user_id)
        await bot.send_message(chat_id=user_id, **band_message)
        return

    band_members = await bands.get_band_members(band_id=band_id)
    if len(band_members) >= Config.Bands.BAND_MEMBERS_LIMIT:
        await bot.send_message(chat_id=user_id, text='В банде нет свободных мест!')
        return

    band_members_scores = await bands.get_sorted_band_members_with_scores(band_id=band_id)
    await bot.send_message(
        chat_id=user_id,
        text=BandsMessages.get_ask_for_join_band(band=band, band_creator=band.creator, members_scores=band_members_scores),
        reply_markup=BandsKeyboards.get_join_band(band_id=band_id)
    )


# endregion


async def handle_bands_button(message: Message):
    menu_message_data = await __get_bands_menu_message_data(for_user_id=message.from_user.id)
    await message.answer(**menu_message_data)


# МОЯ БАНДА
async def handle_cancel_band_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    menu_message_data = await __get_bands_menu_message_data(for_user_id=callback.from_user.id)
    await callback.message.answer(**menu_message_data)
    await state.clear()


async def handle_create_band_callback(callback: CallbackQuery, state: FSMContext):
    user_band = await bands.get_user_band(telegram_id=callback.from_user.id)
    if user_band:
        await callback.answer(f'❗Вы не можете вступить в эту банду, '
                              f'так как уже являетесь участником банды {user_band.title}')
        band_message = await __get_user_band_message_data(band_id=user_band.id, user_id=callback.from_user.id)
        await callback.message.edit_text(**band_message)
        return

    await callback.message.edit_text(
        text='Введите название банды: ',
        reply_markup=BandsKeyboards.get_back_to_bands_menu()
    )
    await state.set_state(BandCreationStates.enter_band_title)


async def handle_new_band_title_message(message: Message, state: FSMContext):
    # Проверяем корректность названия
    band_title = await get_title_or_send_error(title_message=message)
    if not band_title:
        return

    created_band = await bands.create_band(creator_telegram_id=message.from_user.id, title=band_title)

    await message.answer('✅ Банда создана!')
    menu_message_data = await __get_user_band_message_data(band_id=created_band.id, user_id=message.from_user.id)
    await message.answer(**menu_message_data)
    await state.clear()


async def handle_back_to_bands_menu(callback: CallbackQuery):
    menu_message_data = await __get_bands_menu_message_data(for_user_id=callback.from_user.id)
    try:
        await callback.message.edit_text(**menu_message_data)
    except TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer(**menu_message_data)


async def handle_show_my_band(callback: CallbackQuery, callback_data: BandCallback):
    user_band = await bands.get_user_band(telegram_id=callback.from_user.id)

    if user_band and user_band.id == callback_data.band_id:
        band_message_data = await __get_user_band_message_data(
            band_id=callback_data.band_id, user_id=callback.from_user.id
        )
        await callback.message.edit_text(**band_message_data)


async def handle_rename_band(callback: CallbackQuery, callback_data: BandCallback, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await state.update_data(band_id=callback_data.band_id)
    await callback.message.answer(
        text='Введите новое название банды:',
        reply_markup=BandsKeyboards.get_back_to_bands_menu()
    )
    await state.set_state(BandEditStates.edit_band_title)


async def handle_new_band_title(message: Message, state: FSMContext):
    data = await state.get_data()
    band_id = data.get('band_id')

    band_title = await get_title_or_send_error(title_message=message)
    if not band_title:
        return
    await bands.update_band_title(band_id=band_id, new_title=band_title)

    await message.answer('✅ Название банды изменено')
    band_message_data = await __get_user_band_message_data(band_id=band_id, user_id=message.from_user.id)
    await message.answer(**band_message_data)
    await state.clear()


async def handle_kick_members_from_band(callback: CallbackQuery, callback_data: BandCallback):
    is_band_creator = await bands.is_user_is_band_creator(band_id=callback_data.band_id, user_id=callback.from_user.id)
    if not is_band_creator:
        return await callback.answer('Вы не являетесь создателем этой банды!')

    members = await bands.get_band_members(band_id=callback_data.band_id)
    members = [member for member in members if member.telegram_id != callback.from_user.id]

    if len(members) == 0:
        await callback.answer('Вы - единственный участник банды!')
        return

    await callback.message.edit_text(
        text=BandsMessages.ask_for_member_to_kick(),
        reply_markup=BandsKeyboards.get_kick_members(band_id=callback_data.band_id, members=members)
    )


async def handle_kick_member(callback: CallbackQuery, callback_data: BandMemberCallback):
    await bands.kick_member_from_band(user_id=callback_data.user_id, band_id=callback_data.band_id)
    await callback.answer(text='Участник исключён', show_alert=True)

    members = await bands.get_band_members(band_id=callback_data.band_id)
    members = [member for member in members if member.telegram_id != callback.from_user.id]
    if len(members) == 0:
        band_message_data = await __get_user_band_message_data(
            band_id=callback_data.band_id, user_id=callback.from_user.id
        )
        await callback.message.edit_text(**band_message_data)
        return

    await callback.message.edit_reply_markup(
        reply_markup=BandsKeyboards.get_kick_members(band_id=callback_data.band_id, members=members)
    )


async def handle_join_band_callback(callback: CallbackQuery, callback_data: BandCallback):
    user_band = await bands.get_user_band(telegram_id=callback.from_user.id)
    if user_band:
        await callback.answer(f'Вы уже являетесь участником банды {user_band.title}')
        band_message = await __get_user_band_message_data(band_id=user_band.id, user_id=callback.from_user.id)
        await callback.message.edit_text(**band_message)
        return

    try:
        await bands.add_member_to_band(telegram_id=callback.from_user.id, band_id=callback_data.band_id)
    except Exception as e:
        print(e)

    await callback.answer('🎉 Поздравляю! Ты стал участником банды!', show_alert=True)
    await callback.message.delete()
    bands_menu_message_data = await __get_bands_menu_message_data(for_user_id=callback.from_user.id)
    await callback.message.answer(**bands_menu_message_data)


async def handle_leave_band(callback: CallbackQuery, callback_data: BandCallback):
    await bands.kick_member_from_band(band_id=callback_data.band_id, user_id=callback.from_user.id)
    await callback.answer('Вы покинули банду', show_alert=True)
    bands_menu = await __get_bands_menu_message_data(for_user_id=callback.from_user.id)
    await callback.message.edit_text(**bands_menu)


async def handle_delete_band(callback: CallbackQuery, callback_data: BandCallback):
    await callback.message.edit_text(
        text='❗ Вы уверены, что хотите распустить банду? \nВернуть всё, как было, не получится.',
        reply_markup=BandsKeyboards.get_consider_delete_band(band_id=callback_data.band_id)
    )


async def handle_consider_delete_band(callback: CallbackQuery, callback_data: BandCallback):
    await bands.delete_band(band_id=callback_data.band_id)
    await callback.answer('Ваша банда была распущена.', show_alert=True)
    bands_menu_message_data = await __get_bands_menu_message_data(for_user_id=callback.from_user.id)
    await callback.message.edit_text(**bands_menu_message_data)


async def handle_band_opponents(callback: CallbackQuery, callback_data: BandCallback):
    user_band = await bands.get_band_by_id(band_id=callback_data.band_id)
    opponents = await bands.get_band_opponents(player_band=user_band)

    await callback.message.edit_text(
        text='Соперники вашей банды:',
        reply_markup=BandsKeyboards.get_band_competitors(user_band, opponents)
    )


# РЕЙТИНГ БАНД
async def handle_rating_callback(callback: CallbackQuery):
    bands_rating = await bands.get_bands_global_rating(count=10)

    user_band = await bands.get_user_band(telegram_id=callback.from_user.id)
    user_band_rank = await bands.get_band_rating_position(target_band=user_band)
    markup = BandsKeyboards.get_global_rating(bands_rating, user_band, user_band_rank)

    await callback.message.edit_text(text='📊 Рейтинг банд', reply_markup=markup)


# ГОРОД

async def handle_city_callback(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer_photo(
        caption='🗺 Карта города <b>BarredLand</b>', reply_markup=BandsKeyboards.get_city(),
        photo=BandsMessages.get_global_map_photo()
    )
    # await callback.message.edit_media()


async def handle_band_map_callback(callback: CallbackQuery, callback_data: BandsMapCallback):
    if callback_data.league == callback_data.current_league:
        await callback.answer()
        return

    map_photo = await get_bands_map_photo_file_id(league=callback_data.league)

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=map_photo,
        reply_markup=BandsKeyboards.get_city(current_league=callback_data.league),
        caption=str(callback_data.league)
    )


# ИНФОРМАЦИЯ

async def handle_info_callback(callback: CallbackQuery):
    await callback.message.edit_text(text='ℹ Информация о бандах', reply_markup=BandsKeyboards.get_info())


async def handle_info_article_callback(callback: CallbackQuery, callback_data: MenuNavigationCallback):
    text = ''

    match callback_data.option:
        case 'leagues_rules': text = BandsMessages.get_leagues_rules_explanation()
        case 'rewards': text = BandsMessages.get_rewards_explanation()
        case 'bands_rules': text = BandsMessages.get_bands_rules_explanation()
        case 'city_rules': text = BandsMessages.get_city_rules_explanation()

    await callback.message.edit_text(text=text, reply_markup=BandsKeyboards.get_back_to_info())


def register_bands_handlers(router: Router):
    router.message.register(handle_bands_button, F.text.lower().contains('банды'))
    router.callback_query.register(
        handle_cancel_band_creation,
        MenuNavigationCallback.filter((F.branch == 'bands') & ~F.option),
        StateFilter(BandCreationStates, BandEditStates)
    )
    router.callback_query.register(
        handle_back_to_bands_menu, MenuNavigationCallback.filter((F.branch == 'bands') & ~F.option),
    )

    # Вступить в банду
    router.callback_query.register(handle_join_band_callback, BandCallback.filter(F.action == 'join'))

    # Создать банду
    router.callback_query.register(
        handle_create_band_callback,
        MenuNavigationCallback.filter((F.branch == 'bands') & (F.option == 'create'))
    )
    router.message.register(handle_new_band_title_message, BandCreationStates.enter_band_title)

    # Моя банда
    router.callback_query.register(handle_show_my_band, BandCallback.filter(~F.action))  # Показать

    router.callback_query.register(handle_rename_band, BandCallback.filter(F.action == 'rename'))  # Переименовать
    router.message.register(handle_new_band_title, BandEditStates.edit_band_title)

    router.callback_query.register(handle_kick_members_from_band, BandCallback.filter(F.action == 'kick'))
    router.callback_query.register(handle_kick_member, BandMemberCallback.filter(F.action == 'kick'))  # Исключить

    router.callback_query.register(handle_leave_band, BandCallback.filter(F.action == 'leave'))  # Покинуть

    router.callback_query.register(handle_delete_band, BandCallback.filter(F.action == 'delete'))  # Удалить
    router.callback_query.register(  # Подтверждение удалить
        handle_consider_delete_band, BandCallback.filter(F.action == 'final_delete')
    )

    router.callback_query.register(handle_band_opponents, BandCallback.filter(F.action == 'competitors'))  # Соперники

    # Рейтинг
    router.callback_query.register(
        handle_rating_callback, MenuNavigationCallback.filter((F.branch == 'bands') & (F.option == 'rating'))
    )

    # Город
    router.callback_query.register(
        handle_city_callback, MenuNavigationCallback.filter((F.branch == 'bands') & (F.option == 'city'))
    )
    router.callback_query.register(handle_band_map_callback, BandsMapCallback.filter())

    # Информация
    router.callback_query.register(
        handle_info_callback, MenuNavigationCallback.filter((F.branch == 'bands') & (F.option == 'info'))
    )
    router.callback_query.register(
        handle_info_article_callback,
        MenuNavigationCallback.filter(
            (F.branch == 'bands') & (F.option.in_(['leagues_rules', 'rewards', 'bands_rules', 'city_rules']))
        )
    )
