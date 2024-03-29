import random

from src.messages.user.games.game_messages_abc import CreatableGamesMessages, BotGamesMessagesBase
from src.utils.text_utils import format_float_to_rub_string


class BowlingMessages(BotGamesMessagesBase, CreatableGamesMessages):

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        texts = (
            'Вот он, сладкий звук падающих кегль! \nТы зашел в зал Боулинга!',
            'Крик "Страйк!" разносится по всему залу. Ты явно хочешь составить компанию этим счастливчикам.',
            'DICY: Стой! Правил что ли не знаешь? Куда в обуви? \n'
            'Сначала переобуйся, а потом уже сможешь выбивать страйки.',
            'DICY: Сбивать кегли — это целая наука. \nСейчас посмотрим на твои навыки, ученый.',
            'DICY: Держу в курсе, не только ты страйк хочешь выбить. Одно ясно — твоя удача не бесконечна.',
        )
        return random.choice(texts)

    @staticmethod
    def get_ask_for_bet_photo() -> str:
        return 'https://telegra.ph/file/636d71c96544b2c9741ed.png'

    @staticmethod
    def get_game_created(game_number: int):
        return CreatableGamesMessages.get_game_created(game_number=game_number)

    @staticmethod
    def get_game_started():
        texts = (
            'DICY: Постарайся разбежаться и хорошо так бросить шар',
            'DICY: Давай, покажи своё мастерство!',
            'DICY: Бросай скорее! Я на тебя поставил!',
            'DICY: Пожалуйста, только не поскользнись на паркете, а то всякое бывает. Бросай!',
            'DICY: Выбирай шар себе по размеру и скорее бросай! Я уже заждался',
            'DICY: Хорош выжидать момент. Разбежался и бросил — ничего сложного!',
        )
        return random.choice(texts)

    @staticmethod
    def get_tie():
        texts = (
            'Твой шар сбил столько же кеглей, сколько и шар соперника. \nСтавки возвращаются.',
            'DICY: Ничья! Такое тоже случается. \nТебе вернули ставку.',
            'DICY: Хм, редко такое случается, когда сбивают одинаковое кеглей. \nНичья, поэтому тебе вернули ставку',
            'DICY: Можешь пока что выдохнуть, ничья. \nТебе вернули твою ставку.',
        )
        return random.choice(texts)

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        texts = (
            'Как только ты сбиваешь больше кеглей, чем соперник, тебе сразу несут выигрыш {amount}',
            'Шар попал точно в цель, и ты сбил больше кеглей, чем соперник. \nТы сразу забираешь выигрыш {amount}',
            'DICY: Ну ты красавец! Оправдал мою веру в тебя. \nСкорее бери свой выигрыш {amount}!',
            'DICY: Как же ты хорош! Сбил больше кеглей, чем соперник, поэтому с гордостью бери свой выигрыш {amount}!',
            'DICY: А вот и победа! Мои поздравления, ты сегодня в ударе, поэтому греби свой выигрыш {amount}',
            'DICY: Сладкий вкус победы, чувствуешь его? \nЖелаю ощущать его как можно чаще в этом городе. Бери свой выигрыш {amount}!'
        )
        return random.choice(texts).format(amount=format_float_to_rub_string(win_amount))

    @staticmethod
    def get_player_loose():
        texts = (
            'Когда ты разбегался, мяч выскользнул из руки и бросок получился не из лучших. \nТы проиграл.',
            'Увы, но ты сбил меньше кеглей, чем соперник. \nМожет в следующий раз повезёт. \nТы проиграл.',
            'DICY: Да, не быть тебе королем боулинга. \nПо крайней мере, в этот раз. \nТы проиграл.',
            'DICY: Этот бросок у тебя не удался. \nПопробуй в следующий раз. \nТы проиграл.',
            'DICY: Да уж, а заходил такой уверенный! \nЗапомни, не всегда тебе достается всё, что пожелаешь. \nТы проиграл!',
            'DICY: Как? Я же на тебя поставил! Ладно, еще отыграешься. \nТы проиграл.'
        )
        return random.choice(texts)
