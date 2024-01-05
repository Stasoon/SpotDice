from aiogram import Router
from aiogram.filters.command import CommandObject, Command
from aiogram.types import Message

from src.database import games, transactions
from src.keyboards import UserPublicGameKeyboards
from src.messages import UserPublicGameMessages
from src.misc import GameType, GameCategory
from src.utils.game_validations import validate_create_game_cmd


async def create_game_and_send(message: Message, command: CommandObject, game_type: GameType, users_count: int):
    bet = float(command.args.split()[0])

    game = await games.create_game(
        creator_telegram_id=message.from_user.id,
        max_players=users_count,
        game_type=game_type,
        chat_id=message.chat.id,
        game_category=GameCategory.BASIC,
        bet=bet
    )

    await transactions.deduct_bet_from_user_balance(game=game, user_telegram_id=message.from_user.id, amount=bet)

    game_start_message = await message.answer(
        text=await UserPublicGameMessages.get_game_in_chat_created(game, message.chat.username),
        reply_markup=await UserPublicGameKeyboards.get_join_game_in_chat(game),
        parse_mode='HTML'
    )

    await games.update_message_id(game, game_start_message.message_id)


# в словарь добавлять в формате 'команда': GameType
game_type_map = {
    'dice': GameType.DICE,
    'darts': GameType.DARTS,
    'basket': GameType.BASKETBALL,
    'foot': GameType.FOOTBALL,
    'bowl': GameType.BOWLING,
    'slots': GameType.CASINO,
}


@validate_create_game_cmd(args_count=1)
async def handle_games_for_two_players_commands(message: Message, command: CommandObject):
    await create_game_and_send(message, command, game_type=game_type_map.get(command.command), users_count=2)


@validate_create_game_cmd(args_count=1)
async def handle_games_for_three_players_commands(message: Message, command: CommandObject):
    # отсекаем последний символ, отвечающий за количество игры
    game_type = game_type_map.get(command.command[:-1])
    await create_game_and_send(message, command, game_type=game_type, users_count=3)


def register_games_for_two_commands_handlers(router: Router):
    # Игры для двух игроков
    router.message.register(
        handle_games_for_two_players_commands,
        # распаковываем ключи команд для создания игр для двоих
        Command(*game_type_map.keys())
    )

    # Игры для трёх игроков
    postfix_for_three_players_commands = '3'
    commands_for_three_players = [f'{cmd}{postfix_for_three_players_commands}' for cmd in game_type_map.keys()]
    router.message.register(
        handle_games_for_three_players_commands,
        # распаковываем ключи команд для создания игр для двоих
        Command(*commands_for_three_players)
    )
