import json

import asyncio
import os.path
from random import randint

from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums.dice_emoji import DiceEmoji

from src.utils.logging import logger
from src.database.games import even_uneven
from src.database import transactions
from src.keyboards.user.games import EvenUnevenKeyboards
from src.misc.enums.games_enums import EvenUnevenBetOption, GameCategory
from src.messages.user.games import EvenUnevenMessages
from src.utils.text_utils import format_float_to_rub_string

data_file_name = 'even_uneven_data.json'


def get_formatted_time(seconds: int = 0):
    return f"{seconds // 60:02}:{seconds % 60:02}"


def get_won_bet_options(dice_values: tuple[int, int]) -> list[EvenUnevenBetOption]:
    """Возвращает строку с кодовыми названиями опций, которые победили исходя из значений на костях"""
    won_options = []
    a, b = dice_values

    if a + b < 7:
        won_options.append(EvenUnevenBetOption.LESS_7)
    if a + b == 7:
        won_options.append(EvenUnevenBetOption.EQUALS_7)
    if a + b > 7:
        won_options.append(EvenUnevenBetOption.GREATER_7)
    if (a + b) % 2 == 0:
        won_options.append(EvenUnevenBetOption.EVEN)
    if (a + b) % 2 != 0:
        won_options.append(EvenUnevenBetOption.UNEVEN)
    if a == b:
        won_options.append(EvenUnevenBetOption.A_EQUALS_B)

    return won_options


class EvenUneven:
    def __init__(self, bot: Bot, chat_id: int, round_number: int):
        self.bot = bot
        self.chat_id = chat_id
        self.round_number = round_number

        self.__round_message_ids = []
        self.markup = None

    async def __timer(
            self,
            message_to_edit: Message,
            template: str,
            seconds: int = 300, delta_seconds: int = 10
    ):
        chat_id = message_to_edit.chat.id
        msg_id = message_to_edit.message_id
        while seconds > 0:
            await asyncio.sleep(delta_seconds)

            seconds -= delta_seconds
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=self.markup,
                text=template.format(get_formatted_time(seconds=seconds))
            )
        # Удаляем сообщение с таймером
        await self.bot.delete_message(chat_id=chat_id, message_id=msg_id)

    async def __accrue_winnings_and_notify_players(self, won_bet_options):
        player_bets = await even_uneven.get_players_bets()
        winnings_sum = 0

        for bet in player_bets:
            player_id = (await bet.player.get()).telegram_id
            await even_uneven.delete_player_bet(player_id=player_id)

            if bet.option in won_bet_options:
                win_amount = await transactions.accrue_winnings(
                    winner_telegram_id=player_id, game_category=GameCategory.EVEN_UNEVEN,
                    amount=bet.amount * bet.option.get_coefficient()
                )
                winnings_sum += win_amount
                text = EvenUnevenMessages.get_player_won(bet_option=bet.option, amount=win_amount)
            else:
                text = EvenUnevenMessages.get_player_loose(bet=bet.option)
            await self.bot.send_message(chat_id=player_id, text=text, parse_mode='HTML')

        return winnings_sum

    async def edit_stats_message(self):
        text = await EvenUnevenMessages.get_top()
        stats_msg = await self.bot.send_message(
            chat_id=self.chat_id, text=text, parse_mode='HTML', disable_notification=True
        )
        self.__round_message_ids.append(stats_msg.message_id)

    async def __send_round_start_and_start_timer(self, round_number: int):
        seconds_to_wait = randint(2, 4) * 60 - 1

        # Отправляем сообщение
        template = EvenUnevenMessages.get_timer_template(round_number=round_number)
        bot_username = (await self.bot.get_me()).username
        self.markup = EvenUnevenKeyboards.get_bet_options(round_number=round_number, bot_username=bot_username)

        msg = await self.bot.send_message(
            chat_id=self.chat_id,
            text=template.format(get_formatted_time(seconds_to_wait)),
            reply_markup=self.markup
        )

        with open(data_file_name, 'r') as file:
            data = json.load(file)
        data['message_id'] = msg.message_id
        with open(data_file_name, 'w') as file:
            json.dump(data, file, indent=4)

        # Запускаем таймер
        await self.__timer(
            message_to_edit=msg, template=template,
            seconds=seconds_to_wait
        )

    async def __send_dices_and_get_values(self) -> list[int, int]:
        self.__round_message_ids.append(
            (await self.bot.send_message(chat_id=self.chat_id, text='🎲 Бросаем кубики')).message_id
        )

        values = []
        for _ in range(2):
            dice_msg = await self.bot.send_dice(chat_id=self.chat_id, emoji=DiceEmoji.DICE)
            values.append(dice_msg.dice.value)
            self.__round_message_ids.append(dice_msg.message_id)

        self.__round_message_ids.append(
            (await self.bot.send_message(chat_id=self.chat_id, text='Выигрыши начислены')).message_id
        )
        return values

    async def process_round(self):
        # Создаём раунд
        await self.__send_round_start_and_start_timer(self.round_number)

        # Бросаем кости и получаем победившие ставки
        results = await self.__send_dices_and_get_values()
        won_bet_options = get_won_bet_options(results)

        await self.__accrue_winnings_and_notify_players(won_bet_options=won_bet_options)

    async def clear_round_messages(self):
        # Удаляем сообщения, присланные за раунд
        for msg_id in self.__round_message_ids:
            try:
                await self.bot.delete_message(chat_id=self.chat_id, message_id=msg_id)
            except TelegramBadRequest:
                continue


async def start_even_uneven_loop(bot: Bot, channel_id: int):
    if not os.path.exists(data_file_name):
        with open(data_file_name, 'w') as data_file:
            json.dump(
                obj={
                    'round_number': 1,
                    'stats_message_id': None,
                    'message_id': None,
                    'chat_id': channel_id
                },
                fp=data_file, indent=4
            )

    while True:
        with open(data_file_name, 'r') as data_file:
            data = json.load(data_file)

        even_uneven_round = EvenUneven(
            bot=bot, chat_id=channel_id,
            round_number=data.get('round_number')
        )

        try:
            await even_uneven_round.edit_stats_message()
            await even_uneven_round.process_round()
        except Exception as e:
            logger.error(e)

        # Ждём, чтобы игроки увидели результаты
        seconds_btw_rounds = 10
        await asyncio.sleep(seconds_btw_rounds)

        data['round_number'] += 1
        with open(data_file_name, 'w') as file:
            json.dump(obj=data, fp=file, indent=4)
        await even_uneven_round.clear_round_messages()
