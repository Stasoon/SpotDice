import asyncio
from datetime import timedelta, datetime

from aiogram import Bot
from aiogram.exceptions import AiogramError

from settings import Config
from src.database.models import Game, GameStartConfirm
from src.database.games import games
from src.keyboards import UserMenuKeyboards
from src.misc import GameStatus
from src.database.transactions import bet_refunds


async def make_refund_and_notify_players(bot: Bot, game: Game) -> None:
    canceled_text = f'Не все участники подтвердили игру {game.game_type.value} №{game.number}, поэтому она была отменена.'
    markup = UserMenuKeyboards.get_main_menu()

    for player_id in await games.get_player_ids_of_game(game=game):
        await bet_refunds.make_bet_refund(player_id=player_id, amount=game.bet, game=game)
        try:
            await bot.send_message(chat_id=player_id, text=canceled_text, reply_markup=markup)
        except AiogramError:
            pass
        await asyncio.sleep(0.05)


async def cancel_not_confirmed_game(bot: Bot, game: Game):
    await games.cancel_game(game=game)
    chat_id = game.chat_id if game.chat_id < 0 else Config.Games.GAME_CHAT_ID

    try:
        await bot.delete_message(chat_id=chat_id, message_id=game.message_id)
    except AiogramError:
        pass


async def delete_unconfirmed_games(bot: Bot):

    while True:
        threshold_time = datetime.now() - timedelta(minutes=2)
        unconfirmed_games: list[Game] = await Game.filter(
            status=GameStatus.WAIT_FOR_CONFIRM,
            time_started__lt=threshold_time
        )

        for game in unconfirmed_games:
            confirmations = await GameStartConfirm.filter(game=game)

            if len(confirmations) < game.max_players:
                await cancel_not_confirmed_game(bot=bot, game=game)
                await make_refund_and_notify_players(bot=bot, game=game)

        await asyncio.sleep(2*60)

