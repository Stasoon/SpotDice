import random

from src.messages.user.games.game_messages_abc import CreatableGamesMessages, BotGamesMessagesBase
from src.utils.text_utils import format_float_to_rub_string


class DartsMessages(BotGamesMessagesBase, CreatableGamesMessages):

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        texts = (
            'Пришла пора вспомнить, как ты в отеле на юге попадал в яблочко. ',
            'DICY: Пора собрать всю твою удачу и выбить все утроение 20!',
            'DICY: Перед броском дротика тебе надо глубоко вздохнуть и расслабиться. \nТогда точно попадешь!',
            'DICY: Давай, у тебя 3 попытки, чтобы попасть в яблочко! \nВерю в тебя.',
        )
        return random.choice(texts)

    @staticmethod
    def get_game_created(game_number: int):
        return CreatableGamesMessages.get_game_created(game_number=game_number)

    @staticmethod
    def get_ask_for_bet_photo() -> str:
        return 'https://telegra.ph/file/628dc2d1249589bcd4ea4.png'

    @staticmethod
    def get_game_started():
        texts = (
            'DICY: Давай, покажи своё мастерство!',
            'DICY: Пусть удача благоволит тебе. Бросай!',
            'Вдох, Выдох, Бросок!',
        )
        return random.choice(texts)

    @staticmethod
    def get_tie():
        texts = (
            'DICY: Ни тебе, ни сопернику. Ничья! \nСтавки возвращены.',
            'DICY: В целом, не худший расклад для тебя. \nНичья, твоя ставка возвращена',
            'DICY: Пока что выдохни, ничья. \nТак как счет равный, ставки возвращаются.',
            'DICY: Ты и не проиграл, но и не выиграл. Ничья, твоя ставка возвращается.',
        )
        return random.choice(texts)

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0):
        texts = (
            'DICY: Вот это бросок! Ты победил. \nБери свой выигрыш {amount}',
            'DICY: Мастерство не пропьёшь! Ты победил, поэтому бери свой выигрыш {amount}!',
            'DICY: Как же ты хорош! Поздравляю с победой! \nБери свой выигрыш {amount}',
            'DICY: А вот и удача подвалила! Забирай свой выигрыш {amount}',
            'DICY: Отличный бросок! Как хорошо, что на тебя поставил! И мне деньги, и тебе. Бери выигрыш {amount}',
        )
        return random.choice(texts).format(amount=format_float_to_rub_string(win_amount))

    @staticmethod
    def get_player_loose():
        texts = (
            'DICY: Ну как так? Бросок вообще никуда не годится. Ты проиграл.',
            'DICY: Ну, лучшим тоже иногда не везет, ты проиграл.',
            'DICY: А вот и твоя удача закончилась, пошли неудачи. Ты проиграл.',
            'DICY: Окей, иногда можно и дать насладится вкусом победы и другому игроку.',
        )
        return random.choice(texts)
