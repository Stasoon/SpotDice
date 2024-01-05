from datetime import datetime, timedelta
from io import BytesIO
from typing import Type
from collections import defaultdict

import matplotlib.pyplot as plt
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile

from src.database.models import Withdraw, Deposit
from src.utils.text_utils import format_float_to_rub_string


async def get_transaction_data(start_date, end_date, model: Deposit | Withdraw):
    transactions = await model.filter(timestamp__gte=start_date, timestamp__lte=end_date).order_by('timestamp')
    transaction_amounts = defaultdict(int)

    for transaction in transactions:
        date = str(transaction.timestamp.date())
        transaction_amounts[date] += transaction.amount

    return transaction_amounts


async def get_method_frequency(model: Type[Deposit | Withdraw], start_date, end_date):
    transactions = await model.filter(timestamp__gte=start_date, timestamp__lte=end_date).order_by('timestamp')
    method_frequency = defaultdict(int)

    for transaction in transactions:
        method_frequency[transaction.method] += 1

    return method_frequency


async def get_stats_image(days_back: int):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    # Создайте словарь для агрегации сумм по датам
    deposit_amounts = await get_transaction_data(start_date, end_date, Deposit)
    withdraw_amounts = await get_transaction_data(start_date, end_date, Withdraw)

    # Создайте полный список дат в заданном диапазоне
    all_dates = [str((start_date + timedelta(days=i)).date()) for i in range(days_back + 1)]

    # Заполните суммы для дат, когда не было пополнений
    deposit_amounts_list = [deposit_amounts[date] for date in all_dates]
    withdraw_amounts_list = [withdraw_amounts[date] for date in all_dates]

    deposit_method_frequency = await get_method_frequency(Deposit, start_date, end_date)
    withdraw_method_frequency = await get_method_frequency(Withdraw, start_date, end_date)

    fig, axs = plt.subplots(1, 3, figsize=(16, 9), gridspec_kw={'width_ratios': [3, 1, 1]})

    # Левый подграфик (график пополнений и выводов)
    axs[0].plot(all_dates, deposit_amounts_list, label='Пополнения', marker='o', color='blue')
    axs[0].plot(all_dates, withdraw_amounts_list, label='Выводы', marker='o', color='red')
    plt.setp(axs[0].xaxis.get_majorticklabels(), rotation=45)
    axs[0].set_ylabel('Сумма')
    axs[0].legend()
    axs[0].grid(True)
    # axs[0].xaxis.set_major_locator(plt.MaxNLocator(nbins=30))
    axs[0].yaxis.set_major_locator(plt.MaxNLocator(nbins=20))

    # Правый подграфик (круговая диаграмма для частоты использования методов платежа)
    axs[1].pie(
        deposit_method_frequency.values(), labels=[m.value if hasattr(m, 'value') else 'Админ' for m in deposit_method_frequency.keys()],
        autopct='%1.1f%%', startangle=140
    )
    axs[1].set_title('Методы пополнения')

    axs[2].pie(
        withdraw_method_frequency.values(), labels=[m.value if hasattr(m, 'value') else 'Админ' for m in withdraw_method_frequency.keys()],
        autopct='%1.1f%%', startangle=140
    )
    axs[2].set_title('Методы вывода')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer.read()


async def get_stats(model: Type[Deposit | Withdraw], days_back: int):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    transactions = (
        await model
        .filter(timestamp__gte=start_date, timestamp__lte=end_date)
        .prefetch_related('user')
        .order_by('timestamp')
    )

    global_sum = sum(t.amount for t in transactions)
    unique_count = len({t.user.telegram_id for t in transactions})

    return (
        f"{f'➕ Пополнения' if model == Deposit else '➖ Выводы'} средств за {days_back} дней \n\n"
        f"Общая сумма: {format_float_to_rub_string(global_sum)} \n"
        f"Количество транзакций: {len(transactions)} \n"
        f"От разных пользователей: {unique_count}"
    )


async def __handle_show_transactions_stats(message: Message):
    intervals = (1, 7, 30)
    transaction_types = (Deposit, Withdraw)

    for i in intervals:
        text = "\n\n\n".join([await get_stats(model=model, days_back=i) for model in transaction_types])
        photo = BufferedInputFile(file=await get_stats_image(i), filename='stats.jpg')
        await message.answer_photo(caption=text, photo=photo)


def register_statistics_handlers(router: Router):
    router.message.register(__handle_show_transactions_stats, F.text == '📊 Статистика 📊')
