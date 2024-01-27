from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InputMediaPhoto

from src.database import games
from src.database import users
from src.database.games import mines
from src.database.transactions import bets, winnings
from src.keyboards.user.games import MinesKeyboards
from src.messages import GameErrors, BalanceErrors
from src.messages.user.games.mines import MinesMessages
from src.misc.callback_factories import MinesCallback, GamesCallback, MinesCreationCallback
from src.misc.enums.games_enums import GameCategory, GameType


def adjust_value(action: str, current_value: int | float, min_value: int | float, max_value: int | float) -> int | float:
    if action.startswith('-') and current_value > min_value:
        return current_value - 1
    elif action.startswith('+') and current_value < max_value:
        return current_value + 1
    elif action.startswith('min'):
        return min_value
    elif action.startswith('/2'):
        n = current_value // 2
        return n if n > min_value else min_value
    elif action.startswith('*2'):
        n = current_value * 2
        return n if n < max_value else max_value
    elif action.startswith('max'):
        return max_value
    else:
        return current_value


def calculate_coefficient(mines_count: int, opened_cells_count: int) -> float:
    cells_count = 25
    n = cells_count - mines_count - opened_cells_count
    if n == 0:
        n += 1
    coefficient = (1 + cells_count / n - (mines_count/(opened_cells_count+1))**(1/8)) * (opened_cells_count**0.1)
    return round(coefficient, 2)


async def finish_mines_game(telegram_id: int):
    user = await users.get_user_or_none(telegram_id=telegram_id)
    if not user:
        return

    mines_game_data = await mines.get(user=user)
    await games.finish_game(game=mines_game_data.game)
    await mines.delete(user=user)


async def handle_mines_category_callback(callback: CallbackQuery):
    text = MinesMessages.get_category_description(player_name=callback.from_user.first_name)
    markup = MinesKeyboards.get_create_or_back()
    photo = MinesMessages.get_category_photo()

    if callback.message.photo:
        await callback.message.edit_media(media=InputMediaPhoto(media=photo, caption=text), reply_markup=markup)
    else:
        await callback.message.edit_text(text=text, reply_markup=markup)


# region Создание игры

async def handle_create_mines_callback(callback: CallbackQuery):
    user_active_game = await games.get_user_unfinished_game(callback.from_user.id)
    if user_active_game:
        await callback.answer(text=GameErrors.get_another_game_not_finished(user_active_game))
        return

    default_mines_count = 5
    default_bet = 15.0

    text = MinesMessages.get_setup_game()
    markup = MinesKeyboards.get_creation(mines_count=default_mines_count, bet=default_bet)
    await callback.message.edit_caption(caption=text, reply_markup=markup)


async def handle_change_mines_count_callback(callback: CallbackQuery, callback_data: MinesCreationCallback):
    await callback.answer()

    min_mines_count, max_mines_count = 3, 24

    new_value = adjust_value(
        action=callback_data.action, current_value=callback_data.mines_count,
        min_value=min_mines_count, max_value=max_mines_count
    )
    callback_data.mines_count = new_value

    markup = MinesKeyboards.get_creation(mines_count=callback_data.mines_count, bet=callback_data.bet)
    try: await callback.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest: pass


async def handle_change_bet_callback(callback: CallbackQuery, callback_data: MinesCreationCallback):
    await callback.answer()

    min_bet = 15.0
    max_bet = round(await users.get_user_balance(telegram_id=callback.from_user.id)) - 1
    max_bet = max_bet if max_bet > min_bet else min_bet  # если баланс меньше минимальной ставки

    new_value = adjust_value(
        action=callback_data.action, current_value=callback_data.bet,
        min_value=min_bet, max_value=max_bet
    )
    callback_data.bet = new_value

    markup = MinesKeyboards.get_creation(mines_count=callback_data.mines_count, bet=callback_data.bet)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except TelegramBadRequest:
        pass


async def handle_start_mines_callback(callback: CallbackQuery, callback_data: MinesCreationCallback):
    user = await users.get_user_or_none(telegram_id=callback.from_user.id)

    if not user:
        return
    if user.balance < callback_data.bet:
        await callback.answer(text=BalanceErrors.get_low_balance())
        return
    active_game = await games.get_user_unfinished_game(telegram_id=callback.from_user.id)
    if active_game:
        await callback.answer(GameErrors.get_another_game_not_finished(user_active_game=active_game))
        return

    # Создаём игру и списываем деньги с баланса
    game = await games.create_game(
        creator_telegram_id=callback.from_user.id,
        max_players=1, game_category=GameCategory.MINES, game_type=GameType.MINES,
        bet=callback_data.bet, chat_id=callback.from_user.id, message_id=None
    )
    await mines.create(user=user, game=game, mines_count=callback_data.mines_count)
    await bets.deduct_bet_from_user_balance(user_telegram_id=callback.from_user.id, amount=game.bet, game=game)

    next_move_coefficient = calculate_coefficient(mines_count=callback_data.mines_count, opened_cells_count=1)
    markup = MinesKeyboards.get_hidden_mines(mines_count=callback_data.mines_count, next_coefficient=next_move_coefficient)

    winning_without_move = winnings.calculate_amount_with_commission(amount=game.bet)
    MinesKeyboards.update_current_winning(old_markup=markup, winning_amount=winning_without_move)
    await callback.message.edit_caption(caption='Игра началась!', reply_markup=markup)


# endregion


# region Игровой процесс
async def handle_mine_callback(callback: CallbackQuery, callback_data: MinesCallback):
    await callback.answer('🤯')
    await finish_mines_game(telegram_id=callback.from_user.id)

    markup = MinesKeyboards.get_unlocked_field(
        old_markup=callback.message.reply_markup,
        explosion_coordinates=(int(callback_data.x), int(callback_data.y))
    )
    await callback.message.edit_caption(caption='<b>Ты нарвался на мину!</b>', reply_markup=markup)


async def handle_free_callback(callback: CallbackQuery, callback_data: MinesCallback):
    user = await users.get_user_or_none(telegram_id=callback.from_user.id)
    game_data = await mines.get(user)
    cells_opened = await mines.increase_opened_cells(game_data)

    MinesKeyboards.open_cell(callback.message.reply_markup, x=callback_data.x, y=callback_data.y)
    if cells_opened == MinesKeyboards.quad_len**2 - game_data.mines_count:
        await handle_take_winning_callback(callback=callback)
        return

    MinesKeyboards.update_opened_cells_count(
        callback.message.reply_markup, opened_count=cells_opened, mines_count=game_data.mines_count)

    current_coefficient = calculate_coefficient(mines_count=game_data.mines_count, opened_cells_count=cells_opened)
    next_coefficient = calculate_coefficient(mines_count=game_data.mines_count, opened_cells_count=cells_opened + 1)
    MinesKeyboards.update_coefficients(
        callback.message.reply_markup, current_coefficient=current_coefficient, next_coefficient=next_coefficient
    )
    winning_amount = winnings.calculate_amount_with_commission(amount=game_data.game.bet * current_coefficient)
    MinesKeyboards.update_current_winning(old_markup=callback.message.reply_markup, winning_amount=winning_amount)
    await callback.message.edit_reply_markup(reply_markup=callback.message.reply_markup)


async def handle_take_winning_callback(callback: CallbackQuery):
    user = await users.get_user_or_none(telegram_id=callback.from_user.id)
    game_data = await mines.get(user)
    await finish_mines_game(telegram_id=callback.from_user.id)

    win_coefficient = calculate_coefficient(mines_count=game_data.mines_count, opened_cells_count=game_data.cells_opened)
    await winnings.accrue_winnings(
        winner_telegram_id=callback.from_user.id,
        amount=game_data.game.bet * win_coefficient,
        game_category=GameCategory.MINES
    )

    markup = MinesKeyboards.get_unlocked_field(old_markup=callback.message.reply_markup)
    await callback.message.edit_caption(text='Ты выиграл!', reply_markup=markup)


# endregion


def register_mines_handlers(router: Router):
    router.callback_query.register(handle_mines_category_callback, GamesCallback.filter(
        (F.action == 'show') & (F.game_category == GameCategory.MINES) & (F.game_type == GameType.MINES)
    ))

    # Создание игры
    router.callback_query.register(handle_create_mines_callback, MinesCreationCallback.filter(F.action == 'create'))

    router.callback_query.register(  # Изменение количества бомб
        handle_change_mines_count_callback,
        MinesCreationCallback.filter(F.action.contains('bombs'))
    )
    router.callback_query.register(  # Изменение ставки
        handle_change_bet_callback,
        MinesCreationCallback.filter(F.action.contains('bet'))
    )

    router.callback_query.register(
        handle_start_mines_callback, MinesCreationCallback.filter(F.action == 'start')
    )

    router.callback_query.register(
        handle_free_callback, MinesCallback.filter((F.is_mine == 'False') & (F.is_opened == 'False'))
    )
    router.callback_query.register(
        handle_mine_callback, MinesCallback.filter((F.is_mine == 'True') & (F.is_opened == 'False'))
    )

    router.callback_query.register(
        handle_take_winning_callback, MinesCreationCallback.filter(F.action == 'take_winning')
    )
