import random

from src.utils.text_utils import format_float_to_rub_string
from .game_messages_abc import GameCategoryMessages, BotGamesMessagesBase, CreatableGamesMessages


class BlackJackMessages(BotGamesMessagesBase, CreatableGamesMessages, GameCategoryMessages):

    @staticmethod
    def get_category_photo() -> str:
        return 'https://telegra.ph/file/2806e7b6f70fe443f6d87.png'

    @staticmethod
    def get_category_description(player_name: str) -> str:
        texts = (
            'DICY: {player_name}, рад тебя видеть! \nЕсли честно, думал, что у тебя кишка тонка зайти сюда и сесть за один стол с другими игроками. \nУдачной игры и постарайся не остаться в одних трусах.',
            'DICY: Кого я вижу, {player_name}! \nСадись за любой игровой стол и побеждай. \nЖелаю удачи и, пожалуйста, не продай золотую подвеску своей матери ради "Еще одной ставочки"',
            'DICY: {player_name}, а вот и ты! \nХочешь по-быстрому подняться и купить всё, о чём мечтаешь? \nТы в правильном месте. Учитывай только то, что у других те же самые намерения. \nА все богатыми не будут...',
            'DICY: Пароль! Не знаешь пароля — не будет тебе казино. \nЛааадно, шучу) Заходи конечно! \nТолько не разгроми тут от злости ничего, а то до конца жизни будешь залоги выплачивать за золотой интерьер.',
            'Открывая роскошную дверь казино ты видишь просторный зал, где все так и хотят поймать удачу за хвост. \nВпрочем, у тебя такие же намерения, не так ли?',
            'Ты заходишь в главный зал казино, где все дорогие украшения помещения так и говорят тебе: \n"Ты можешь уйти отсюда победителем, а можешь... Лучше об этом не думать!"',
            'Азарт, победы, страсть! \nВсе эти слова сразу же заполоняют твою голову, когда видишь эти игровые столы и выкрики других игроков из главного зала. \nИ ты точно хочешь составить им компанию.',
            '"А что если прямо сейчас поставить всё и выйти победителем?" — именно с этими мыслями ты заходишь в просторный зал казино.',
        )
        return f"♠ BlackJack \n\n{random.choice(texts).format(player_name=player_name)}"

    @staticmethod
    def get_game_created(game_number: int):
        return f'♠ Супер, игра №{game_number} создана! \n\n' \
               f'Скоро к тебе за стол сядет и другой гость нашего заведения. Удачи!'

    @staticmethod
    def ask_for_bet_amount(player_name: str) -> str:
        texts = (
            'Сколько будешь ставить? Просто скажи. \nА если передумал играть, можешь выбрать другую игру. ',
            'Давай не томи, говори свою ставку! \nЕсли одумался, можешь встать со стола и сыграть в другую игру.',
            'Диллер с жадными глазами смотрит на тебя и ожидает твою ставку. ',
            'Сыграть на минимальную ставку или поставить всё? \nРешать тебе.',
            'DICY: Ну что, {player_name}, готов ощутить сладкий вкус победы? \nОн будет слаще, если поставишь больше)',
            'DICY: Чуешь звон монет, {player_name}? \nСкорее ставь и ощути вкус победы.',
            'DICY: {player_name}, смотри, расклад такой: \nНе теряешь голову и спокойно ставишь лесенкой. \nХладнокровно и четко — слова, которые должны тебя описывать.'
        )
        return random.choice(texts).format(player_name=player_name)

    @staticmethod
    def get_game_started(player_name: str = 'дружище') -> str:
        texts = (
            'Игра началась! Жди своего хода, а пока можешь подумать о своей стратегии. \nБудешь ли сразу рисковать или лучше придержишь карты?',
            'Вот и два игрока сели за стол, игра началась! Удачи вам и пусть победит сильнейший! Ожидай своего хода.',
            'Игра началась! Ожидай свою очередь хода. \nНе забывай, что в BlackJack нужно играть с осторожностью, так что вовремя остановись. ДА КОГО Я ОБМАНЫВАЮ, РИСКУЙ И УХОДИ КОРОЛЕМ!',
            'Ты слышишь сладкий звук постукивания фишек о стол. \nИгра началась, жди своего хода.',
            'Игра началась, {player_name}! \nНе подведи меня, я поспорил на твою победу!',
            'А вот и началась игра, {player_name}! \nОжидай своего хода. ',
        )
        return random.choice(texts).format(player_name=player_name)

    @staticmethod
    def get_player_took_card(player_points: int) -> str:
        texts = (
            'Твой счет: {player_points} \n\nDICY: Будешь брать еще?',
            'Твой счёт: {player_points} \n\nDICY: Рискнешь и возьмёшь ещё или струсишь?',
            'Твой счёт: {player_points} \n\nDICY: Решай быстрее, берешь еще карту?',
        )
        return random.choice(texts).format(player_points=player_points)

    @staticmethod
    def get_player_stopped(player_points: int) -> str:
        texts = [
            'Твой счет: {player_points} \n\nDICY: Правильно, надо суметь вовремя остановиться. Ждем других игроков.',
            'Твой счет: {player_points} \n\nDICY: Вовремя остановиться тоже нужно, чтобы потом не проиграть всё. Сейчас подождем других игроков и увидим результаты.',
            'Твой счет: {player_points} \n\nDICY: Ты остался при своих картах. Сейчас увидим, насколько это было мудрое решение.',
        ]
        return random.choice(texts).format(player_points=player_points)

    @staticmethod
    def get_too_much_points(player_points: int) -> str:
        texts = (
            'Твой счет: {player_points} \n\nDICY: Эххх.. Перебор. Жадность фраера сгубила!',
            'Твой счет: {player_points} \n\nDICY: Перебор карт! Нужно было набрать 21, а не больше.',
            'Твой счет: {player_points} \n\nDICY: Увы, но ты перебрал карты. Впредь будь аккуратнее.',
        )
        return random.choice(texts).format(player_points=player_points)

    @staticmethod
    def get_game_finished() -> str:
        texts = (
            'Игра завершена! - громко говорит диллер.',
            'Дамы и господа, у нас есть победитель! - объявляет диллер.',
            'DICY: Игра завершилась! Давай взглянем на результаты.',
        )
        return random.choice(texts)

    @staticmethod
    def get_player_won(player_name: str = 'Игрок', win_amount: float = 0) -> str:
        texts = (
            'Ты победил! Поздравляю, вот твой выигрыш: {win_amount}, диллер указывает на теперь уже твою горсть фишек',
            'ПО-БЕ-ДА! Бери свои фишки и радуйся, пока можешь - говорит тебе диллер. \n\nВыигрыш: {win_amount}',
            'DICY: {player_name}, я в тебе и не сомневался, даже до нашего знакомства знал, что ты король. \n\nТвой выигрыш равен {win_amount}',
            'DICY: А вот и мой чемпион! {player_name}, поздравляю тебя, бери свои фишки на сумму {win_amount}',
            'DICY: Это было несложно, да, {player_name}? Держи свой выигрыш: {win_amount} \n\nКак насчет снова почувствовать себя победителем и сыграть еще?',
            'DICY: "Ты никогда не почувствуешь вкус победы, если карты для тебя не больше, чем развлечение" — помни это и бери свои фишки на сумму {win_amount}',
        )
        return random.choice(texts).format(player_name=player_name, win_amount=format_float_to_rub_string(win_amount))

    @staticmethod
    def get_tie():
        texts = (
            'DICY: Интересная ситуация, у тебя столько же очков, сколько и у диллера. \nТвоя ставка возвращена.',
            'Счет диллера равен твоему, поэтому ты слышишь стук своих же фишек, твоя ставка возвращена.',
            'DICY: Скажи спасибо богу Блэк Джека, что он тебя помиловал. \nТвой счет равен счету диллера, поэтому тебе вернули ставку.',
            'DICY: Не знаю, обрадуешься ли ты, но твоя ставка возвращена. \nТвой счет равен счету диллера.',
        )
        return random.choice(texts)

    @staticmethod
    def get_global_tie():
        texts = (
            'DICY: Равный счет у всех! Не помню, когда последний раз такое видел. \nСтавки возвращены!',
            'DICY: Вот это да, оба игрока и диллер набрали одинаковый счет. \nВ таком случае ставки будут возвращены.',
            'DICY: Интересная ситуация... \nПравила гласят, что при таком исходе, когда счет у всех равный, ставки возвращаются.',
        )
        return random.choice(texts)

    @staticmethod
    def get_player_loose():
        texts = (
            'Другой игрок победил. Такое тоже бывает, еще отыграешься, не беспокойся, — утешает тебя диллер.',
            'Победил другой игрок! Он оказался удачливее, или просто придержал нужную карту в рукаве, кто знает...',
            'Победа другого игрока! На этот раз удача на его стороне. Надо бы преподать ему урок и в следующей игре утереть ему нос.',
            'DICY: Что ж, твой соперник победил, а ты проиграл. Двоих победителей это заведение не вытерпит.',
            'DICY: И победил... Не ты! Да, бывает и такое. Не парься, еще отыграешь своё!',
            'DICY: Ты проиграл."Если ты не замечаешь лоха, значит лох - ты". Видимо ты забыл про эту присказку.',
        )
        return random.choice(texts)

    @staticmethod
    def get_global_loose():
        texts = (
            'Все проиграли! \nУчастники за столом переглядываются и с недовольной гримасой принимают этот печальный факт.',
            'DICY: Ха! Не думал, что вы такие неудачники. \nВсе проиграли, а фишки получил я. Идеально!',
            'DICY: Сегодня я гуляю, ведь все за столом проиграли, а фишки забираю я!',
            'DICY: Да уж, и они еще говорят, что хорошо играют. \nНу-ну! Хотя неважно, все проиграли, а ставки забираю я.',
        )
        return random.choice(texts)

    @staticmethod
    def get_dealer_won() -> str:
        texts = (
            'Дамы и господа, у диллера лучший счет! В этот раз оба игрока проиграли свою ставку.',
            'Вот так новость.. И ты, и твой соперник проиграли, ведь счёт у диллера больше. Не печалься, в следующий раз удача будет на твоей стороне!',
            'Товарищи игроки, я забираю себе ваши ставки! - с довольной ухмылкой говорит диллер, ведь его счет лучше счета игроков.',
        )
        return random.choice(texts)

    @staticmethod
    def get_time_left():
        return 'Время на ход вышло!'
