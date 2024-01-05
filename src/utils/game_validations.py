from functools import wraps

from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject
from aiogram.types import Message, CallbackQuery

from settings import Config
from src.database import games, users, transactions, Game
from src.messages import InputErrors, BalanceErrors, GameErrors
from src.misc import GameStatus


async def check_rights_and_cancel_game(event: CallbackQuery | Message, game: Game):
    """ Проверяет, может ли игрок отменить игру. Если может, возвращает ставки и удаляет игру """
    user_id = event.from_user.id
    if isinstance(event, CallbackQuery): message = event.message
    else: message = event

    # игра не найдена
    if not game:
        await event.answer(text=GameErrors.get_game_is_finished(), parse_mode='HTML')
        return
    # не является создателем
    elif user_id != (await game.creator.get()).telegram_id:
        await event.answer(text=GameErrors.get_not_creator_of_game(), parse_mode='HTML')
        return
    # игра начата
    elif game.status != GameStatus.WAIT_FOR_PLAYERS:
        await event.answer(text=GameErrors.get_cannot_delete_game_message_after_start(), parse_mode='HTML')
        return
    # если всё хорошо, отменяем игру
    else:
        if game.message_id:
            try:
                await event.bot.delete_message(chat_id=message.chat.id, message_id=game.message_id)
            except TelegramBadRequest:
                pass
        await games.cancel_game(game)

        for player_id in await games.get_player_ids_of_game(game):
            await transactions.make_bet_refund(player_id=player_id, amount=game.bet, game=game)


def validate_create_game_cmd(args_count: int = 1, min_bet: int = 30):
    """
    Декоратор, который проверяет, что игрок может выполнить команду создания игры.
    Проверки: баланса, аргументов команды, наличия другой активной игры.
    Если игрок не может создать игру, ваша функция не выполнится, а игроку отправится причина ошибки.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, command: CommandObject, *args, **kwargs):
            try:
                cmd_args = command.args.split()
                bet = float(cmd_args[0].replace(',', '.'))
                user_active_game = await games.get_user_unfinished_game(message.from_user.id)
                balance = await users.get_user_balance(telegram_id=message.from_user.id)
            except AttributeError:
                await message.reply(InputErrors.get_cmd_invalid_argument_count(args_count))
            except ValueError:
                await message.reply(InputErrors.get_cmd_arguments_should_be_digit())
            else:
                if bet < min_bet:
                    await message.reply(BalanceErrors.get_bet_too_low(min_bet))
                    return
                elif balance < bet:
                    await message.answer(BalanceErrors.get_low_balance())
                    return
                elif bet >= Config.Payments.MAX_BET:
                    await message.answer(BalanceErrors.get_bet_too_high(Config.Payments.MAX_BET))
                    return
                elif user_active_game:
                    text = GameErrors.get_another_game_not_finished(user_active_game)
                    try:
                        await message.bot.send_message(
                            chat_id=message.chat.id,
                            text=text,
                            reply_to_message_id=user_active_game.message_id
                        )
                    except TelegramBadRequest:
                        await message.answer(text)
                    return
                elif len(cmd_args) != args_count:
                    await message.reply(InputErrors.get_cmd_invalid_argument_count(args_count))
                    return
                elif not all(arg.isdigit() for arg in command.args.split()[1:]):
                    await message.reply(InputErrors.get_cmd_arguments_should_be_digit())
                    return

                return await func(message, command, *args, **kwargs)

        return wrapper

    return decorator


async def validate_and_extract_bet_amount(amount_message: Message) -> float | None:
    """Делает проверку ставки, написанной в сообщении, содержащем только число.
    При некорректно введённых данных / недостатке баланса, отправляет сообщение и возвращает None.
    Если всё хорошо, возвращает float из сообщения"""
    try:
        bet_amount = float(amount_message.text.replace(',', '.'))
    except (ValueError, TypeError):
        await amount_message.answer(InputErrors.get_message_not_number_retry(), parse_mode='HTML')
        return None

    min_bet_amount = Config.Games.min_bet_amount

    if await users.get_user_balance(amount_message.from_user.id) < bet_amount:
        await amount_message.answer(text=BalanceErrors.get_low_balance())
        return None

    if bet_amount < min_bet_amount:
        await amount_message.answer(
            text=BalanceErrors.get_insufficient_transaction_amount(min_bet_amount),
            parse_mode='HTML'
        )
        return None
    elif bet_amount > Config.Payments.MAX_BET:
        await amount_message.answer(BalanceErrors.get_bet_too_high(max_bet=Config.Payments.MAX_BET), parse_mode='HTML')
        return

    return bet_amount


async def validate_join_game_request(callback: CallbackQuery, game: Game) -> bool:
    """Проверяет, что игрок может присоединиться к игре. Если нет, отправляет сообщение и возвращает False \n
    Проверки: баланс для ставки, участие в этой / другой игре, есть ли места"""
    user_id = callback.from_user.id
    balance = await users.get_user_balance(user_id)
    user_active_game = await games.get_user_unfinished_game(user_id)

    # если игра уже закончена
    if game.status in (GameStatus.CANCELED, GameStatus.FINISHED):
        await callback.answer(text=GameErrors.get_game_is_full())
        return False
    # если баланс меньше ставки
    elif balance < game.bet:
        await callback.answer(text=BalanceErrors.get_low_balance(), show_alert=True)
        return False
    # если игрок уже участник
    elif user_id in await games.get_player_ids_of_game(game):
        await callback.answer(text=GameErrors.get_already_in_this_game(), show_alert=True)
        return False
    # если игрок задействован в другой игре
    elif user_active_game:
        await callback.answer(text=GameErrors.get_already_in_other_game(user_active_game), show_alert=True)
        return False
    # если игра уже заполнена
    elif await games.is_game_full(game) or game.status == GameStatus.ACTIVE:
        await callback.answer(text=GameErrors.get_game_is_full(), show_alert=True)
        return False
    await callback.answer('✅ Вы присоединились к игре')
    return True
