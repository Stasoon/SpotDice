from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import transactions
from src.database.games.even_uneven import add_player_bet
from src.keyboards.user.games import EvenUnevenKeyboards
from src.misc.enums.games_enums import EvenUnevenBetOption
from src.misc.states import EnterEvenUnevenBetStates
from src.utils.game_validations import validate_and_extract_bet_amount


def get_bet_option_description(option: EvenUnevenBetOption):
    match option:
        case EvenUnevenBetOption.LESS_7:
            return 'Сумма > 7'
        case EvenUnevenBetOption.EQUALS_7:
            return 'Сумма = 7'
        case EvenUnevenBetOption.GREATER_7:
            return 'Сумма > 7'
        case EvenUnevenBetOption.EVEN:
            return 'Чётное'
        case EvenUnevenBetOption.UNEVEN:
            return 'Нечётное'
        case EvenUnevenBetOption.A_EQUALS_B:
            return 'Первое = Второму'
    return None


async def show_bet_entering(message: Message, state: FSMContext, round_number: int, bet_option: str):
    try:
        option = EvenUnevenBetOption(bet_option)
    except ValueError:
        return

    # option_description = get_bet_option_description(option)
    if not option:
        return

    await message.answer(
        text='Введите сумму ставки:',
        reply_markup=EvenUnevenKeyboards.get_cancel_bet_entering(),
        parse_mode='HTML'
    )
    await state.update_data(round_number=round_number, bet_option=option)
    await state.set_state(EnterEvenUnevenBetStates.wait_for_bet)


async def handle_bet_amount_message(message: Message, state: FSMContext):
    """Обработка сообщения с суммой ставки"""
    data = await state.get_data()
    bet_amount = await validate_and_extract_bet_amount(message)
    if not bet_amount:
        return

    # списываем деньги
    await transactions.deduct_bet_from_user_balance(user_telegram_id=message.from_user.id, amount=bet_amount)

    # сохраняем ставку
    await add_player_bet(player_id=message.from_user.id, amount=bet_amount, option=data.get('bet_option'))

    # отвечаем, что ставка принята
    option_description = get_bet_option_description(data.get("bet_option"))
    await message.answer(
        f'Вы поставили {bet_amount:.2f} рублей на: <b>{option_description}</b>'
    )

    await state.clear()


async def handle_cancel_bet_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


def register_even_uneven_handlers(router: Router):
    # Сообщение со ставкой
    router.message.register(handle_bet_amount_message, EnterEvenUnevenBetStates.wait_for_bet)
    # Отмена ставки
    router.callback_query.register(handle_cancel_bet_callback,
                                   F.data == 'cancel_even_uneven_bet',
                                   EnterEvenUnevenBetStates.wait_for_bet)
