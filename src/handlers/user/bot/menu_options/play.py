from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto

from src.database import users, games, transactions
from src.handlers.user.chat.chat import send_game_created_in_bot_notification
from src.keyboards.user import UserBotGameKeyboards, UserMenuKeyboards
from src.messages import get_full_game_info_text
from src.messages.user import UserMenuMessages, UserPrivateGameMessages, GameErrors
from src.messages.user.games.choose_game_messages import get_message_instance_by_game_type, get_game_category_message_instance
from src.utils.game_validations import validate_and_extract_bet_amount, check_rights_and_cancel_game
from src.misc import MenuNavigationCallback, GamesCallback, GameCategory, GameType, GamePagesNavigationCallback
from src.misc.states import EnterBetStates
from src.utils import logger


# region Utils


async def get_play_message_data(user_id: int) -> dict:
    text = UserMenuMessages.get_play_menu(await users.get_user_or_none(user_id))
    reply_markup = UserBotGameKeyboards.get_play_menu()
    return {'text': text, 'reply_markup': reply_markup, 'parse_mode': 'HTML'}


async def show_game_category(
        to_callback: CallbackQuery, game_category: GameCategory, page_num: int = 0
):
    games_per_page = 6
    offset = page_num * games_per_page

    available_games = await games.get_bot_available_games(
        game_category=game_category, limit=games_per_page, offset=offset,
        for_user_id=to_callback.from_user.id
    )

    if page_num > 0 and len(available_games) < 1:
        await to_callback.answer(UserPrivateGameMessages.get_its_last_page())
        return

    player = await users.get_user_or_none(telegram_id=to_callback.from_user.id)
    if not player:
        return

    message_instance = get_game_category_message_instance(game_category=game_category)
    text = message_instance.get_category_description(player_name=player.name)
    photo = message_instance.get_category_photo()
    markup = await UserBotGameKeyboards.get_game_category(
        available_games=available_games, category=game_category, current_page_num=page_num
    )

    try:
        if to_callback.message.photo:
            await to_callback.message.edit_media(media=InputMediaPhoto(media=photo, caption=text), reply_markup=markup)
        else:
            await to_callback.message.answer_photo(photo=photo, caption=text, reply_markup=markup)
            await to_callback.message.delete()
    except TelegramBadRequest:
        pass
    except Exception as e:
        logger.error(e)


async def show_basic_game_types(to_message: Message):
    await to_message.edit_caption(
        text=UserPrivateGameMessages.get_choose_game_type(),
        reply_markup=UserBotGameKeyboards.get_basic_game_types(),
        parse_mode='HTML'
    )


async def show_bet_entering(callback: CallbackQuery, game_type: GameType, game_category: GameCategory):
    message = callback.message
    await message.delete()

    message_instance = get_message_instance_by_game_type(game_type=game_type)
    text = await UserPrivateGameMessages.enter_bet_amount(
        message_instance=message_instance, user_id=callback.from_user.id, game_type_name=game_type.get_full_name()
    )
    await message.answer(
        text=text, reply_markup=UserBotGameKeyboards.get_cancel_bet_entering(game_category), parse_mode='HTML'
    )


# endregion


# region Handlers

async def handle_play_button(message: Message, state: FSMContext):
    """Обработка кнопки Играть из меню"""
    await state.clear()
    text = UserMenuMessages.get_play_menu(await users.get_user_or_none(message.from_user.id))
    reply_markup = UserBotGameKeyboards.get_play_menu()
    photo = UserMenuMessages.get_play_menu_photo()
    await message.answer_photo(photo=photo, caption=text, reply_markup=reply_markup)


async def handle_game_category_callback(callback: CallbackQuery, callback_data: GamesCallback, state: FSMContext):
    """Обработка нажатия на одну из категорий игр"""
    await state.clear()
    game_category = callback_data.game_category
    await show_game_category(to_callback=callback, game_category=game_category)


async def handle_game_category_stats_callback(callback: CallbackQuery, callback_data: GamesCallback):
    """Показывает статистику по выбранной категории игр"""
    game_category = callback_data.game_category
    await callback.message.edit_caption(
        caption=await UserPrivateGameMessages.get_game_category_stats(game_category),
        reply_markup=UserBotGameKeyboards.get_back_from_stats(game_category),
        parse_mode='HTML'
    )


async def handle_refresh_games_callback(callback: CallbackQuery, callback_data: GamesCallback):
    """Обновление списка доступных игр"""
    try:
        await show_game_category(
            to_callback=callback,  page_num=0,
            game_category=callback_data.game_category,
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


async def handle_cancel_game_callback(callback: CallbackQuery, callback_data: GamesCallback):
    """ Обработка нажатия на кнопку Отменить игру """
    game = await games.get_game_obj(callback_data.game_number)
    await check_rights_and_cancel_game(event=callback, game=game)

    await callback.answer(text=UserPrivateGameMessages.get_game_successfully_canceled())
    await show_game_category(to_callback=callback, game_category=callback_data.game_category)


async def handle_game_pages_navigation_callback(callback: CallbackQuery, callback_data: GamePagesNavigationCallback):
    if callback_data.direction == 'next':
        page_num = callback_data.current_page + 1
    else:
        page_num = callback_data.current_page - 1

    if page_num >= 0:
        await show_game_category(
            to_callback=callback, game_category=callback_data.category, page_num=page_num
        )
    else:
        await callback.answer(UserPrivateGameMessages.get_its_last_page())


async def handle_create_game_callback(callback: CallbackQuery, callback_data: GamesCallback, state: FSMContext):
    """Обработка нажатия на кнопку Создать"""
    user_active_game = await games.get_user_unfinished_game(callback.from_user.id)
    if user_active_game:
        await callback.answer(text=GameErrors.get_another_game_not_finished(user_active_game))
        return

    game_category = callback_data.game_category

    # СЮДА ДОБАВЛЯТЬ СОЗДАНИЕ ИГРЫ
    if game_category == GameCategory.BASIC:
        await show_basic_game_types(callback.message)
    else:
        if game_category == GameCategory.BLACKJACK:
            game_type = GameType.BJ
        elif game_category == GameCategory.BACCARAT:
            game_type = GameType.BACCARAT
        else:
            return

        await show_bet_entering(callback, game_type, game_category)

        await state.update_data(game_category=game_category, game_type=game_type)
        await state.set_state(EnterBetStates.wait_for_bet_amount)


async def handle_basic_game_type_callback(callback: CallbackQuery, callback_data: GamesCallback, state: FSMContext):
    """Обработка нажатия на тип обычной игры при её создании"""
    await show_bet_entering(callback, callback_data.game_type, callback_data.game_category)

    await state.update_data(game_category=callback_data.game_category, game_type=callback_data.game_type)
    await state.set_state(EnterBetStates.wait_for_bet_amount)


async def handle_bet_amount_message(message: Message, state: FSMContext):
    """Обработка сообщения с суммой ставки"""
    bet_amount = await validate_and_extract_bet_amount(message)
    data = await state.get_data()

    if not bet_amount:
        return

    # создаём игру
    created_game = await games.create_game(
        game_category=data.get('game_category'), game_type=data.get('game_type'),
        chat_id=message.chat.id,
        creator_telegram_id=message.from_user.id, max_players=2, bet=bet_amount
    )
    # списываем деньги
    await transactions.deduct_bet_from_user_balance(
        game=created_game, user_telegram_id=message.from_user.id, amount=bet_amount
    )
    # отвечаем, что игра создана
    message_instance = get_message_instance_by_game_type(game_type=created_game.game_type)
    await message.answer(
        text=message_instance.get_game_created(game_number=created_game.number),
        reply_markup=UserMenuKeyboards.get_main_menu(),
        parse_mode='HTML',
    )

    await send_game_created_in_bot_notification(message.bot, created_game)
    await state.clear()


async def handle_show_game_callback(callback: CallbackQuery, callback_data: GamesCallback):
    """Обработка нажатия на доступную игру"""
    game = await games.get_game_obj(callback_data.game_number)
    await callback.message.edit_text(
        text=await get_full_game_info_text(game),
        reply_markup=await UserBotGameKeyboards.get_join_game_or_back(
            user_id=callback.from_user.id, game=game
        ),
        parse_mode='HTML'
    )


async def handle_back_in_play_callback(callback: CallbackQuery):
    text = UserMenuMessages.get_play_menu(await users.get_user_or_none(callback.from_user.id))
    reply_markup = UserBotGameKeyboards.get_play_menu()
    photo = UserMenuMessages.get_play_menu_photo()

    if callback.message.photo:
        await callback.message.edit_media(media=InputMediaPhoto(media=photo, caption=text), reply_markup=reply_markup)
    else:
        await callback.message.answer_photo(photo=photo, caption=text, reply_markup=reply_markup)
        await callback.message.delete()


def register_play_handlers(router: Router):
    router.message.register(handle_play_button, F.text.contains('🎰  Играть  🎰'))

    # показать игру
    router.callback_query.register(handle_show_game_callback, GamesCallback.filter(
        (F.action == 'show') & F.game_number
    ))

    # показать категорию
    router.callback_query.register(handle_game_category_callback, GamesCallback.filter(
        (F.action == 'show') & F.game_category))

    # статистика
    router.callback_query.register(handle_game_category_stats_callback, GamesCallback.filter(
        F.action == 'stats'
    ))

    # обновить игры
    router.callback_query.register(handle_refresh_games_callback, GamesCallback.filter(
        F.action == 'refresh'
    ))

    # отменить игру
    router.callback_query.register(handle_cancel_game_callback, GamesCallback.filter(
        F.action == 'cancel'
    ))

    # навигация по страницам с играми
    router.callback_query.register(handle_game_pages_navigation_callback, GamePagesNavigationCallback.filter())

    # создать игру
    router.callback_query.register(handle_create_game_callback, GamesCallback.filter(
        (F.action == 'create') & ~F.game_type & ~F.game_number
    ))

    router.callback_query.register(handle_basic_game_type_callback, GamesCallback.filter(
        (F.action == 'create') & F.game_type
    ))
    # назад
    router.message.register(handle_bet_amount_message, EnterBetStates.wait_for_bet_amount)

    router.callback_query.register(handle_back_in_play_callback, MenuNavigationCallback.filter(
        (F.branch == 'game_strategies') & ~F.option))
