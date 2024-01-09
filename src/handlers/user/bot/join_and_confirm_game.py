from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from settings import Config
from src.database import Game, transactions
from src.database.games import games
from src.database.models import GameStartConfirm
from src.keyboards import UserBotGameKeyboards, UserMenuKeyboards
from src.misc import GamesCallback, GameCategory, GameStatus
from src.utils.game_validations import validate_join_game_request

from src.handlers.user.bot.game_strategies import BlackJackStrategy, BaccaratStrategy, BasicGameStrategy


# region Utils

async def add_user_to_bot_game(callback: CallbackQuery, game: Game):
    await callback.message.delete()
    await games.add_user_to_game(callback.from_user.id, game.number)

    # если игра заполнилась, перенаправляем на начало нужной игры (в зависимости от категории)
    if await games.is_game_full(game):
        await games.set_wait_for_confirm_status(game=game)

        for player in await games.get_players_of_game(game=game):
            await callback.bot.send_message(
                chat_id=player.telegram_id,
                text='Подтвердите начало игры:',
                reply_markup=UserBotGameKeyboards.get_confirm_game_start()
            )


async def start_game(bot: Bot, game: Game):
    await games.activate_game(game)
    strategy = None

    match game.category:
        case GameCategory.BASIC:
            strategy = BasicGameStrategy
        case GameCategory.BACCARAT:
            strategy = BaccaratStrategy
        case GameCategory.BLACKJACK:
            strategy = BlackJackStrategy

    if strategy:
        try:
            await bot.delete_message(chat_id=game.chat_id, message_id=game.message_id)
        except Exception:
            pass
        await strategy.start_game(bot, game)


# endregion

# region Handlers

async def handle_join_game_callback(callback: CallbackQuery, callback_data: GamesCallback, state: FSMContext):
    # отменяем состояние игрока
    await state.clear()
    game = await games.get_game_obj(callback_data.game_number)

    if await validate_join_game_request(callback, game):
        await add_user_to_bot_game(callback, game)
        await transactions.deduct_bet_from_user_balance(
            game=game, user_telegram_id=callback.from_user.id, amount=game.bet
        )


async def handle_confirm_game_start_button(message: Message):
    game = await games.get_user_unfinished_game(telegram_id=message.from_user.id)

    if game.status != GameStatus.WAIT_FOR_CONFIRM:
        await message.answer('Другой игрок не подтвердил начало игры, поэтому она была отменена.')
        return

    await GameStartConfirm.get_or_create(player_id=message.from_user.id, game=game)
    confirmations = await GameStartConfirm.filter(game=game)

    if len(confirmations) < game.max_players:
        await message.answer(
            text='Хорошо! Подождём, пока соперник подтвердит начало игры...',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        try:
            await message.bot.delete_message(
                chat_id=game.chat_id if game.chat_id < 0 else Config.Games.GAME_CHAT_ID,
                message_id=game.message_id
            )
        except Exception:
            pass
        await start_game(bot=message.bot, game=game)


# endregion


def register_join_game_handlers(router: Router):
    router.callback_query.register(
        handle_join_game_callback,
        GamesCallback.filter((F.action == 'join') & F.game_number)
    )

    router.message.register(
        handle_confirm_game_start_button, F.text == '✅ Начать игру'
    )
