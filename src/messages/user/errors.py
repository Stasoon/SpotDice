from src.utils.text_utils import format_float_to_rub_string
from src.database import Game
from .games import get_game_header


def get_throttling_message() -> str:
    return '🙏 Пожалуйста, не так часто'


class PaymentErrors:
    """Ошибки, связанные с платежами"""
    @staticmethod
    def get_payment_not_found() -> str:
        return '❗Платёж не найден'

    @staticmethod
    def get_payment_system_error() -> str:
        return 'Что-то пошло не так❗ \nПросим прощения. Воспользуйтесь другим способом или обратитесь в поддержку'


class InputErrors:
    """Ошибки, связанные с неправильным вводом (длина / тип)"""
    @staticmethod
    def get_cmd_arguments_should_be_digit() -> str:
        return '❗Аргументами команды должны быть числа!'

    @staticmethod
    def get_cmd_invalid_argument_count(must_be_count: int) -> str:
        last_num = int(str(must_be_count)[-1])
        if last_num == 1:
            return f'❗В команде должен быть {must_be_count} параметр.'
        elif last_num > 4:
            return f'❗В команде должно быть {must_be_count} параметров.'
        else:
            return f'❗В команде должно быть {must_be_count} параметра.'

    @staticmethod
    def get_text_expected_retry() -> str:
        return '❗Это не текст. \nПопробуйте снова:'

    @staticmethod
    def get_message_not_number_retry():
        return '❗Вы ввели не число. \nПопробуйте ещё раз:'

    @staticmethod
    def get_message_text_too_long_retry() -> str:
        return '❗Текст сообщения слишком длинный. \nПопробуйте снова:'

    @staticmethod
    def get_message_text_too_short_retry() -> str:
        return '❗Текст сообщения слишком короткий. \nПопробуйте снова:'

    @staticmethod
    def get_photo_expected_retry() -> str:
        return '❗Это не фотография. \nОтправьте боту скриншот оплаты:'


class BalanceErrors:
    """Ошибки, связанные с размерами чисел и балансом"""
    @staticmethod
    def get_low_balance() -> str:
        return '❌ Недостаточный баланс!'

    @staticmethod
    def get_insufficient_balance(balance: float):
        """На балансе всего <сумма>. Введите другую сумму"""
        return f'❗На вашем балансе всего {format_float_to_rub_string(balance)}. \nВведите другую сумму:'

    @staticmethod
    def get_insufficient_transaction_amount(min_transaction_amount: float) -> str:
        """Сумма транзакции меньше минимальной"""
        return f'❗Минимальная сумма транзакции - {format_float_to_rub_string(min_transaction_amount)}. \n' \
               f'Попробуйте ещё раз:'

    @staticmethod
    def low_balance_for_withdraw(min_withdraw_amount: float):
        return f'⛔Минимальная сумма вывода - {format_float_to_rub_string(min_withdraw_amount, use_html=False)}'

    @staticmethod
    def get_bet_too_low(min_bet: int) -> str:
        return f'❗Минимальная ставка в этой игре - {format_float_to_rub_string(min_bet, use_html=False)} \n' \
               f'Попробуйте ещё раз'

    @staticmethod
    def get_bet_too_high(max_bet: float) -> str:
        return f'❗Максимальная ставка - {format_float_to_rub_string(max_bet, use_html=False)} \n' \
               f'Попробуйте ещё раз'


class GameErrors:
    """Тексты сообщений с ошибками для игр"""
    @staticmethod
    def get_not_registered_in_bot() -> str:
        return f'❗Чтобы играть в чате, сначала зайдите в нашего бота'

    @staticmethod
    def get_no_active_games() -> str:
        return '❌ Активных игр не найдено!'

    @staticmethod
    def get_game_is_finished() -> str:
        return '❌ Игра уже закончилась'

    @staticmethod
    def get_game_is_full() -> str:
        return '❌ В игре нет свободных мест'

    @staticmethod
    def get_not_creator_of_game() -> str:
        return '❗Вы не являетесь создателем этой игры!'

    @staticmethod
    def get_delete_game_time_limit() -> str:
        return '❗Удалить игру можно лишь через полчаса, если никто не зашёл'

    @staticmethod
    def get_cannot_delete_game_message_after_start():
        return '❗Нельзя удалить игру, если она уже началась'

    @staticmethod
    def get_already_in_this_game() -> str:
        return '❗Вы уже участвуете в этой игре'

    @staticmethod
    def get_already_in_other_game(game: Game) -> str:
        return f'❗Вы уже участвуете в {game.game_type.value}№{game.number}'

    @staticmethod
    def get_another_game_not_finished(user_active_game: Game) -> str:
        return f'❗Чтобы начать игру, завершите {get_game_header(game=user_active_game)}'
