import asyncio
from datetime import timedelta, datetime

from aiogram import Bot

from src.database.models import Game, GameStartConfirm
from src.database.games import games
from src.keyboards import UserMenuKeyboards
from src.misc import GameStatus
from src.database.transactions import bet_refunds


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
                game.status = GameStatus.CANCELLED
                await game.save()

                for player_id in await games.get_player_ids_of_game(game=game):
                    await bot.send_message(
                        chat_id=player_id,
                        text=f'Не все игроки подтвердили игру №{game.number}, поэтому она была отменена.',
                        reply_markup=UserMenuKeyboards.get_main_menu()
                    )
                    await bet_refunds.make_bet_refund(player_id=player_id, amount=game.bet, game=game)
                    await asyncio.sleep(0.05)

        await asyncio.sleep(2*60)

