import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ForceReply, ReplyKeyboardRemove

from src.database import games, transactions, Game, User
from src.database.games import game_scores
from src.handlers.user.bot.game_strategies import BlackJackStrategy, BaccaratStrategy
from src.messages.user import UserPublicGameMessages
from src.misc import GamesCallback, GameStatus, GameCategory
from src.utils.game_validations import validate_join_game_request


# region Utils

async def start_chat_game(game: Game, callback: CallbackQuery):
    """Запускает игру в чате"""
    await games.activate_game(game)
    await callback.message.delete()

    markup = ForceReply(selective=True, input_field_placeholder=f'Отправьте {game.game_type.value}')

    match game.category:
        case GameCategory.BLACKJACK:
            await BlackJackStrategy.start_game(callback.bot, game)
        case GameCategory.BACCARAT:
            await BaccaratStrategy.start_game(callback.bot, game)
        case _:
            msg = await callback.message.bot.send_message(
                chat_id=callback.message.chat.id,
                text=await UserPublicGameMessages.get_game_in_chat_start(game),
                reply_markup=markup, parse_mode='HTML'
            )
            await games.update_message_id(game, msg.message_id)


async def join_chat_game(callback: CallbackQuery, game: Game):
    """Добавляет юзера в игру. Если все игроки собраны, запускает игру"""
    await games.add_user_to_game(telegram_id=callback.from_user.id, game_number=game.number)
    await transactions.deduct_bet_from_user_balance(game=game, user_telegram_id=callback.from_user.id, amount=game.bet)

    if len(await games.get_players_of_game(game)) >= game.max_players:
        await start_chat_game(game, callback)
    else:
        text = await UserPublicGameMessages.get_game_in_chat_created(game=game, chat_username=callback.message.chat.username)
        await callback.message.edit_text(text=text, reply_markup=callback.message.reply_markup)


async def process_player_move(game: Game, message: Message):
    """Обрабатывает ход в игре в чате"""
    game_moves = await game_scores.get_game_moves(game)
    player_telegram_id = message.from_user.id
    dice_value = message.dice.value

    # если не все игроки сделали ходы
    if len(game_moves) < game.max_players:
        await game_scores.add_player_move_if_not_moved(game, player_telegram_id=player_telegram_id, move_value=dice_value)

    # если все походили, ждём окончания анимации и заканчиваем игру
    if len(await game_scores.get_game_moves(game)) >= game.max_players:
        await finish_game(game, message)


async def __accrue_players_winnings_and_get_amount(game: Game, win_coefficient: float, winners: list[User]) -> float:
    # Начисляем выигрыши победителям
    winning_with_commission = None

    for winner in winners:
        winning_with_commission = await transactions.accrue_winnings(
            game_category=game.category, winner_telegram_id=winner.telegram_id,
            amount=(game.bet * win_coefficient) / len(winners)
        )
    return winning_with_commission


async def finish_game(game: Game, message: Message):
    if game.status == GameStatus.FINISHED:
        return

    win_coefficient = len(await games.get_players_of_game(game))  # ставка умножается на количество игроков
    game_moves = await game_scores.get_game_moves(game)
    await games.finish_game(game)
    await game_scores.delete_game_scores(game)
    winners = []

    max_move = max(game_moves, key=lambda move: move.value)
    winning_with_commission = None

    if all(move.value == max_move.value for move in game_moves):  # Если значения одинаковы (ничья)
        # Возвращаем деньги участникам
        for move in game_moves:
            player = await move.player.get()
            await transactions.make_bet_refund(player.telegram_id, game=game, amount=game.bet)
    else:  # значения разные
        # формируем список победителей
        winners = [await move.player.get() for move in game_moves if move.value == max_move.value]
        # начисляем выигрыши
        winning_with_commission = await __accrue_players_winnings_and_get_amount(
            game=game, winners=winners, win_coefficient=win_coefficient)

    seconds_to_wait = 3
    await asyncio.sleep(seconds_to_wait)

    text = await UserPublicGameMessages.get_game_in_chat_finish(
        game=game, game_moves=game_moves, winners=winners, win_amount=winning_with_commission
    )
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')

# endregion Utils

# region Handlers


async def handle_game_move_message(message: Message):
    game = await games.get_user_unfinished_game(message.from_user.id)
    dice = message.dice

    # Если игрок есть в игре и тип эмодзи соответствует
    if dice and game and message.reply_to_message \
            and message.reply_to_message.message_id == game.message_id and \
            dice.emoji == game.game_type.value:
        await process_player_move(game, message)


async def handle_join_game_in_chat_callback(callback: CallbackQuery, callback_data: GamesCallback):
    """Обработка на нажатие кнопки Присоединиться к созданной игре в чате"""
    game_number = int(callback_data.game_number)
    game = await games.get_game_obj(game_number=game_number)

    if not await validate_join_game_request(callback, game):
        return

    await join_chat_game(callback, game)


# endregion Handlers

def register_game_actions_handlers(router: Router):
    router.message.register(handle_game_move_message)
    router.callback_query.register(handle_join_game_in_chat_callback, GamesCallback.filter(F.action == 'join'))
