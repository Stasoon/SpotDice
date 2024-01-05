import random

from src.database import get_top_winners_by_amount
from src.misc import GameCategory
from src.misc.enums.games_enums import EvenUnevenBetOption
from src.utils.text_utils import format_float_to_rub_string


class EvenUnevenMessages:
    @staticmethod
    def get_timer_template(round_number: int) -> str:
        return f'🎲 Раунд #{round_number} \n' + \
               '⏱ {} \n♻ Ожидание ставок...'

    @staticmethod
    async def get_top() -> str:
        emoji_numbers = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣')
        top_players = await get_top_winners_by_amount(category=GameCategory.EVEN_UNEVEN, days_back=7, limit=6)
        text = '🏆 Топ победителей: \n\n'
        for n, player in enumerate(top_players, start=1):
            text += f'{emoji_numbers[n]} {str(player)} — {format_float_to_rub_string(player.winnings_amount)}\n'
        return text

    @staticmethod
    def get_player_won(bet_option: EvenUnevenBetOption, amount: float) -> str:
        texts = ('Вы выиграли {amount}',)

        match bet_option:
            case EvenUnevenBetOption.LESS_7:
                texts = (
                    'DICY: Супер! На двух кубах выпало меньше 7, забирай свой заслуженный выигрыш: {amount}',
                    'DICY: Было сложно не победить в этой ставке. \n'
                    'А попробуй с таким же успехом поставить на то, что выпадет ровно 7! \n'
                    'Ну а пока бери свой выигрыш {amount}',
                    'DICY: На кубах выпало меньше 7 очков, скорее бери свой выигрыш {amount}! \n'
                    'А то тут могут и обворовать зевак.'
                )
            case EvenUnevenBetOption.EQUALS_7:
                texts = (
                    'DICY: На двух кубах сумма очков ровно 7! \nА ты хорош, греби свой выигрыш {amount}',
                    'DICY: Ха! Удача на твоей стороне, ведь сумма очков на двух кубах равна 7. \nТы выиграл {amount}',
                    'DICY: Ты поймал удачу за хвост! \nСумма очков на кубах равна 7, а значит ты выиграл {amount}',
                )
            case EvenUnevenBetOption.GREATER_7:
                texts = (
                    'DICY: Удача благоволит тебе, сумма очков больше 7, а значит ты забираешь свой выигрыш {amount}',
                    'DICY: Есть! На двух кубах сумма очков больше 7, греби свой выигрыш {amount}',
                    'DICY: Ну тебе просто повезло, на двух кубах сумма очков больше 7. \n'
                    'Спорим, что в следующий раз не победишь? \nТы выиграл {amount}',
                )
            case EvenUnevenBetOption.EVEN:
                texts = (
                    'DICY: Чёткая! Ой, точнее Чётная сумма на кубах. \n'
                    'В любом случае все чётко, бери свой выигрыш {amount}',
                    'DICY: На кубах чётная сумма, а значит ты можешь радоваться, ведь выиграл {amount}',
                    'DICY: Да обычное везение, в этот раз боги рандома помиловали тебя: на кубах чётная сумма. \n'
                    'Но вот в следующий раз... \nБери уже свой выигрыш: {amount}',
                )
            case EvenUnevenBetOption.UNEVEN:
                texts = (
                    'DICY: Опа, а вот и праздник на твоей улице! Сумма кубов нечётная, бери свой выигрыш {amount}',
                    'DICY: Так так! На игровом столе сумма кубов нечётная, а значит ты победил! Твой выигрыш {amount}',
                    'DICY: Поздравляю тебя, на столе сумма кубов нечётная! \n'
                    'Сегодня ты гуляешь, бери свой выигрыш {amount}',
                )
            case EvenUnevenBetOption.A_EQUALS_B:
                texts = (
                    'DICY: Ну такую удачу я давно не видел! \n'
                    'Одинаковые числа утроили твою ставку. \nТы забираешь {amount}',
                    'DICY: Как же тебе везёт! \n'
                    'Одинаковые числа на кубах позволили тебе утроить твою ставку, забирай {amount}',
                    'DICY: Вау! Знаешь, почему твоя ставка утроилась? \n'
                    'Числа на кубах равные, греби свой выигрыш {amount}',
                )

        return random.choice(texts).format(amount=format_float_to_rub_string(amount))

    @staticmethod
    def get_player_loose(bet: EvenUnevenBetOption) -> str:
        texts = ('<b>🎲 Вы проиграли</b>',)

        match bet:
            case EvenUnevenBetOption.LESS_7:
                texts = (
                    'DICY: Увы, но на этот раз на кубах значение больше 7. \nНадо было делать другую ставку.',
                    'DICY: Вот и удачи твоей не стало. \nНа кубах больше 7!',
                    'DICY: К сожалению для тебя и к счастью для меня, выпало больше 7! \n'
                    'Пойду на твои деньги закажу еще золота для главного зала казино.',
                )
            case EvenUnevenBetOption.EQUALS_7:
                texts = (
                    'DICY: Увы, на кубах сумма очков не 7, ты проиграл. \nМожет в следующий раз повезет больше.',
                    'DICY: Ты проиграл! \nА на что ты рассчитывал, когда ставил на такой редкий исход?',
                    'DICY: Эххх, не получилась сорвать куш. \nНо ты можешь попробовать еще раз.',
                )
            case EvenUnevenBetOption.GREATER_7:
                texts = (
                    'DICY: Да, кубы сегодня скупы на числа, выпала сумма меньше 7, а значит ты остался без денег.',
                    'DICY: Иии... На двух кубах выпало меньше 7, поэтому ты проиграл. \nТвоя удача, видимо, закончилась.',
                    'DICY: Советую тебе провериться на сглаз, так не везти просто не может! \nТы проиграл.',
                )
            case EvenUnevenBetOption.EVEN:
                texts = (
                    'DICY: Немного не угадал, сумма на кубах нечётная. \nТы проиграл.',
                    'DICY: Сумма нечётная и это совсем не чётко для тебя. \nВ этот раз ты проиграл.',
                    'DICY: Какая досада, сумма на кубах нечётная! \nТы проиграл! Не передать, как мне тебя жаль! \n'
                    'Ну иди поплачь, может поможет.',
                )
            case EvenUnevenBetOption.UNEVEN:
                texts = (
                    'DICY: Да уж, не повезло сегодня тебе. \nНе получилось угадать то, что сумма кубов будет нечётная.',
                    'DICY: Как же так? Не угадал... Какое горе. \nА я радуюсь, теперь твои деньги — мои деньги.',
                    'DICY: Не получилось сегодня у тебя ухватить удачу за хвост, сумма кубов на игровом столе чётная.',
                )
            case EvenUnevenBetOption.A_EQUALS_B:
                texts = (
                    'DICY: Ну а что ты хотел, когда ставил на исход одинаковых значений? \n'
                    'Деньги на ветер, прямо мне в карман!',
                    'DICY: Ну что сказать, ты пытался. \nМожет когда-то и выпадут одинаковые числа... Не в этой жизни.',
                    'DICY: Если честно, не знаю, что у тебя было в голове, когда ты ставил на этот исход. \n'
                    'Увы, но удача вообще не на твоей стороне.',
                )

        return random.choice(texts)
