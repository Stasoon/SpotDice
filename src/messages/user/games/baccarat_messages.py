import random
from typing import Collection

from src.database import PlayerScore
from src.messages.user.games.creatable_game_messages_base import CreatableGamesMessages
from src.messages.user.games.game_messages_base import BotGamesMessagesBase
from src.misc.enums import BaccaratBettingOption


class BaccaratMessages(CreatableGamesMessages, BotGamesMessagesBase):
    @staticmethod
    def get_game_started():
        texts = (
            'DICY: Сейчас ты выбираешь, на кого поставить.',
            'DICY: Чего ты ждешь? Скорее ставь и жди результатов этой игры, я уже хочу поздравить победителя!',
            'DICY: Поставь либо на Игрока, либо на Банкира, либо же на Ничью',
        )
        return random.choice(texts)

    @staticmethod
    def get_tie():
        pass

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        texts = (
            'DICY: Победа, Победа! Ты правильно поставил, а значит забирай свой выигрыш {win_amount}',
            'DICY: Твоя ставка оказалась выигрышной! Скорее бери свой выигрыш {win_amount}',
            'DICY: Поздравляю с победой, ты сделал правильную ставку. Бери свой выигрыш {win_amount}',
        )
        return random.choice(texts).format(win_amount=win_amount)

    @staticmethod
    def get_player_loose():
        texts = (
            'DICY: Слушай, всем иногда не везет, так что прими поражение достойно. ',
            'DICY: А ты так уверенно поставил... \nНу что ж, и проигрыши случаются.',
            'DICY: Ты проиграл. Грустно, досадно, но что поделать? \nВ следующий раз повезет!',
        )
        return random.choice(texts)

    @staticmethod
    def get_game_created(game_number: int):
        return f'🎴 Игра Baccarat №{game_number} создана!'

    @staticmethod
    def get_category_description(player_name: str) -> str:
        texts = (
            'DICY: Приветствую! Это еще одна карточная игра, которая может испытать твою удачу. \nЧто может быть лучше?',
            'DICY: Баккарат — это такая карточная игра, которая может оставить в дураках обоих игроков, но  и выиграть тоже могут все.',
            'DICY: Добро пожаловать в Баккарат! Скажу тебе по секрету, это моя любимая игра. \nВедь проиграть могут сразу оба игрока!',
        )
        return f'🎴 Baccarat \n\n{random.choice(texts)}'

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        return 'Сколько будешь ставить?'

    @staticmethod
    async def get_baccarat_results(bet_choices: Collection[PlayerScore]):
        text = 'Результаты \n\n'
        for choice in bet_choices:
            text += f'{await choice.player.get()} — '
            match choice.value:
                case BaccaratBettingOption.PLAYER.value:
                    text += 'игрок \n'
                case BaccaratBettingOption.BANKER.value:
                    text += 'банкир \n'
                case BaccaratBettingOption.TIE.value:
                    text += 'ничья \n'
                case _:
                    text += 'пропустил ход'
        return text
