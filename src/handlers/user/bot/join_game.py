from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.database import games, Game, transactions
from src.misc import GamesCallback, GameCategory
from src.utils.game_validations import validate_join_game_request

from src.handlers.user.bot.game_strategies import BlackJackStrategy, BaccaratStrategy, BasicGameStrategy


# region Utils

async def add_user_to_bot_game(callback: CallbackQuery, game: Game):
    await callback.message.delete()
    await games.add_user_to_game(callback.from_user.id, game.number)

    # если игра заполнилась, перенаправляем на начало нужной игры (в зависимости от категории)
    if await games.is_game_full(game):
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
            await strategy.start_game(callback.bot, game)


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

# endregion


def register_join_game_handlers(router: Router):
    router.callback_query.register(handle_join_game_callback, GamesCallback.filter(
        (F.action == 'join') & F.game_number
    ))
