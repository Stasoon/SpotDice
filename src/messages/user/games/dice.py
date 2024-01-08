import random

from src.messages import UserPrivateGameMessages
from src.messages.user.games.creatable_game_messages_base import CreatableGamesMessages
from src.messages.user.games.game_messages_base import BotGamesMessagesBase
from src.utils.text_utils import format_float_to_rub_string


class DiceMessages(BotGamesMessagesBase, CreatableGamesMessages):
    @staticmethod
    def get_game_started():
        return 'Игра началась. \nБросай кости!'

    @staticmethod
    def get_tie():
        texts = (
            'DICY: В этой схватке сразились два равных игрока, ничья! \nСтавки возвращены.',
            'DICY: Ставки возвращаются, у игроков одинаковый счёт! \nСразитесь снова, чтобы выявить победителя.',
            'DICY: Все так хотели выиграть, что в итоге случилась ничья. Ставки возвращены.',
            'DICY: Ничья! Так как у игроков одинаковый счет, ставки возвращаются.',
        )
        return random.choice(texts)

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        texts = (
            'DICY: Сегодня удача на твоей стороне, скорее бери свой выигрыш {amount}!',
            'DICY: Ты победил! На твоем месте я бы испытал удачу еще раз. \nВ любом случае, бери свой выигрыш {amount}',
            'DICY: Как же тебя везет! \nТвоего счета на костях достаточно, чтобы победить. \nВот твой выигрыш: {amount}',
            'DICY: Победа твоя! Забирай {amount}. \nКак я понял, ты сегодня проставляешься, не так ли?',
        )
        return random.choice(texts).format(amount=format_float_to_rub_string(win_amount))

    @staticmethod
    def get_player_loose():
        texts = (
            'DICY: Увы, но в этот раз ты не ушёл победителем. \nСчёт соперника больше.',
            'DICY: Упс... Ты проиграл, а твой соперник уже забрал свой выигрыш. \nНевезение случается.',
            'DICY: Ты проиграл. Скажу по опыту: такое случается, когда неуверен в себе. \n'
            'Или просто Боги великого Рандома не благоволят тебе сегодня.',
            'DICY: Выиграть было весьма просто. \nНужно было просто выкинуть больше очков! \nНо ты проиграл.',
        )
        return random.choice(texts)

    @staticmethod
    def get_category_description(player_name: str) -> str:
        pass

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        texts = (
            'DICY: Да, ты все верно понял! Это игра имени меня! \nУдачи тебе!',
            'DICY: В игре в кости главное сосредоточиться и собрать всю удачу в кулак!',
            'DICY: Добро пожаловать в главную игру — кости! \nСкажу по секрету, мне в нее всегда везет.',
        )
        return random.choice(texts)

    @staticmethod
    def get_game_created(game_number: int):
        return UserPrivateGameMessages.get_game_created(game_number=game_number)
