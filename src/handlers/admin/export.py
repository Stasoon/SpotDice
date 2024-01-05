import csv
import io
import os
from uuid import uuid4

from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import BufferedInputFile

from src.database.users import User, get_all_users


def get_users_csv(users: list[User]) -> io.BytesIO:
    filename = f"{uuid4().int}.csv"

    with open(filename, 'w', encoding='utf-8-sig', newline='') as file:
        fieldnames = ["telegram id", "name", "username", "balance", "registration data", "bot blocked"]

        writer = csv.DictWriter(file, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()

        for user in users:
            writer.writerow({
                "telegram id": user.telegram_id,
                "name": user.name,
                "username": user.username,
                "balance": float(user.balance),
                "registration data": user.registration_date,
                "bot blocked": user.bot_blocked
            })

    output = io.BytesIO()
    with open(filename, 'rb') as file:
        output.write(file.read())
    os.remove(filename)

    output.seek(0)
    return output


def get_user_ids_txt(users: list[User]) -> io.BytesIO:
    filename = f"{uuid4().int}.txt"

    with open(filename, 'w', encoding='utf-8') as file:
        for user in users:
            file.write(f'{user.telegram_id}\n')

    output = io.BytesIO()
    with open(filename, 'rb') as file:
        output.write(file.read())
    os.remove(filename)

    output.seek(0)
    return output


async def handle_export_data_button(message: Message):
    users = await get_all_users()

    users_csv_content = get_users_csv(users).read()
    user_ids_txt_content = get_user_ids_txt(users).read()

    await message.answer_document(
        document=BufferedInputFile(file=users_csv_content, filename='users.csv')
    )
    await message.answer_document(
        document=BufferedInputFile(file=user_ids_txt_content, filename='user_ids.txt')
    )

    # await message.answer_document(document=get_games_csv())


def register_data_export_handlers(router: Router):
    router.message.register(handle_export_data_button, F.text.lower().contains('экспорт данных'))
