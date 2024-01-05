from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.database import games, transactions, Game
from src.handlers.user.bot.game_strategies import BaccaratStrategy, BlackJackStrategy
from src.keyboards import UserPublicGameKeyboards
from src.messages import UserPublicGameMessages
from src.misc import GameType, GameCategory
from src.utils.game_validations import validate_create_game_cmd


async def __send_game_created(message: Message, created_game: Game):
    bot_username = (await message.bot.get_me()).username

    # отправляем сообщение о том, что игра создана
    game_start_message = await message.answer(
        text=await UserPublicGameMessages.get_game_created_in_bot_notification(created_game, bot_username),
        reply_markup=await UserPublicGameKeyboards.get_go_to_bot_and_join(created_game, bot_username),
        parse_mode='HTML'
    )
    # сохраняем сообщение в базе данных за начатой игрой
    await games.update_message_id(game=created_game, new_message_id=game_start_message.message_id)


async def create_game_and_deduct_bet(
        user_id: int, chat_id: int, bet_amount: float,
        game_category: GameCategory, game_type: GameType, max_players: int = 2
):
    """
    Создаёт игру с указанными параметрами и списывает размер ставки с баланса создателя.
    Возвращает созданную игру
    """
    created_game = await games.create_game(
        game_category=game_category, game_type=game_type,
        chat_id=chat_id,
        creator_telegram_id=user_id, max_players=max_players, bet=bet_amount
    )

    # списываем деньги
    await transactions.deduct_bet_from_user_balance(
        game=created_game, user_telegram_id=user_id, amount=bet_amount
    )

    return created_game


# region Handlers

@validate_create_game_cmd(args_count=1)
async def handle_create_black_jack_cmd(message: Message, command: CommandObject):
    # получаем ставку
    bet_amount = float(command.args)

    # создаём игру и списываем ставку с баланса создателя
    created_game = await create_game_and_deduct_bet(
        user_id=message.from_user.id, chat_id=message.chat.id,
        bet_amount=bet_amount,
        game_category=GameCategory.BLACKJACK, game_type=GameType.BJ
    )

    await __send_game_created(message=message, created_game=created_game)


@validate_create_game_cmd(args_count=1)
async def handle_create_baccarat_cmd(message: Message, command: CommandObject):
    # получаем ставку
    bet_amount = float(command.args)

    # создаём игру и списываем ставку с баланса создателя
    created_game = await create_game_and_deduct_bet(
        user_id=message.from_user.id, chat_id=message.chat.id, bet_amount=bet_amount,
        game_category=GameCategory.BACCARAT, game_type=GameType.BACCARAT
    )

    await __send_game_created(message=message, created_game=created_game)


# endregion


def register_card_games_handlers(router: Router):
    router.message.register(handle_create_black_jack_cmd, Command('bj'))
    router.message.register(handle_create_baccarat_cmd, Command('baccarat'))

    BaccaratStrategy.register_moves_handlers(router)
    BlackJackStrategy.register_moves_handlers(router)
