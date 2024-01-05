import asyncio

from aiogram import Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters.command import CommandObject, Command
from aiogram.types import Message

from src.database import games, transactions, Game
from src.messages.user import UserPublicGameMessages
from src.misc import GameType, GameCategory
from src.utils.game_validations import validate_create_game_cmd


# region Utils

async def start_mini_game(game_start_msg: Message, game_start_cmd: CommandObject, game_type: GameType) -> Game:
    bet = float(game_start_cmd.args.split()[0])
    user_id = game_start_msg.from_user.id

    # создаём игру
    game = await games.create_game(
        creator_telegram_id=user_id, max_players=1, bet=bet,
        chat_id=game_start_msg.chat.id, message_id=game_start_msg.message_id,
        game_type=game_type, game_category=GameCategory.BASIC)
    # списываем сумму ставки
    await transactions.deduct_bet_from_user_balance(game=game, user_telegram_id=user_id, amount=bet)
    return game


async def process_mini_game_result(user_message: Message, game: Game, win_coefficient: int = 0):
    """В win_coefficient передать коэффициент выигрыша, или 0 при проигрыше"""
    if win_coefficient:
        winning_amount = game.bet * win_coefficient
        await user_message.answer(text=UserPublicGameMessages.get_mini_game_victory(game, winning_amount),
                                  parse_mode='HTML')
        await games.finish_game(game)
        await transactions.accrue_winnings(
            game_category=game.category, winner_telegram_id=user_message.from_user.id, amount=winning_amount
        )
    else:
        await user_message.answer(UserPublicGameMessages.get_mini_game_loose(game=game), parse_mode='HTML')
        await games.finish_game(game)

# endregion


# region MiniGames

@validate_create_game_cmd(args_count=2)
async def handle_cube_command(message: Message, command: CommandObject):
    if not 1 <= int(command.args.split()[-1]) <= 6:
        await message.answer('❗Можно поставить только на числа с 1 по 6')
        return

    game = await start_mini_game(message, command, GameType.DICE)

    user_choice = command.args.split()[1]
    dice_message = await message.reply_dice(DiceEmoji.DICE)
    await asyncio.sleep(4)

    # если угадал, то выигрыш = ставка * 2.5
    win_coefficient = 2.5 if user_choice == str(dice_message.dice.value) else 0
    await process_mini_game_result(message, game, win_coefficient)


@validate_create_game_cmd(args_count=1, min_bet=10)
async def handle_casino_command(message: Message, command: CommandObject):
    game = await start_mini_game(message, command, GameType.CASINO)

    dice_message = await message.reply_dice(DiceEmoji.SLOT_MACHINE)
    await asyncio.sleep(2)

    dice_value = dice_message.dice.value
    # во сколько раз умножится выигрыш
    win_coefficient = 0
    if dice_value in (6, 11, 16, 17, 27, 32, 33, 38, 48, 49, 54, 59):  # Первые 2
        win_coefficient = 1.5
    if dice_value in (1, 22, 43):  # Первые 3
        win_coefficient = 2.25
    elif dice_value == 64:  # Три семёрки (джек-пот)
        win_coefficient = 5

    await process_mini_game_result(message, game, win_coefficient)


def register_mini_games_handlers(router: Router):
    # MiniGames
    router.message.register(handle_cube_command, Command('cube'))
    router.message.register(handle_casino_command, Command('casino'))
