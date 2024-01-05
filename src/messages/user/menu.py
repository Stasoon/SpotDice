import random

from aiogram import html

from src.database import transactions, User, users, get_total_games_count, get_total_users_count, bands
from src.database.transactions import referral_bonuses
from src.database.transactions.bets import get_total_bets_sum
from src.misc.enums.leagues import BandLeague
from src.utils.text_utils import format_float_to_rub_string


class UserMenuMessages:

    @staticmethod
    def get_welcome(user_name: str = 'незнакомец') -> str:
        return f"👋 Привет, {html.bold(html.quote(user_name))}!"

    @staticmethod
    def get_welcome_sticker() -> str:
        stickers = (
            'CAACAgIAAxkBAAIeE2WXbhUtjQ3cMteg1wxI5MK6NdguAAKEPQACjb6pSPbkiqaCZlawNAQ',
            'CAACAgIAAxkBAAIeFGWXbuxrns2NnF3HPAnfSJkQUBfEAAKbOgACfqSJSm6moJb_jUEUNAQ',
            'CAACAgIAAxkBAAECKcpll289p75DflvG23RG4TZ5ni3i9wAC6UEAAjKGSEtfcMDufg0AAeM0BA'
        )
        return random.choice(stickers)

    @staticmethod
    def get_user_agreement_animation() -> str:
        return 'https://telegra.ph/file/39827678fc24d72d687f1.mp4'

    @staticmethod
    def get_play_menu(user: User) -> str:
        balance_str = html.code(format_float_to_rub_string(user.balance))
        return f'👤 Вы в игровом меню \n🪙 Баланс: {balance_str} \n\n/deposit — нажми, чтобы пополнить баланс'

    @staticmethod
    def get_events() -> str:
        return '📰 Наши события'

    @staticmethod
    async def get_referral_system(bot_username: str, user_id: int) -> str:
        percent_to_referrer = await referral_bonuses.calculate_referral_bonus_percent(user_id=user_id)
        user_referrals_count = await users.get_referrals_count_by_telegram_id(user_id)
        earned_amount = format_float_to_rub_string(await transactions.get_referral_earnings(user_id))

        return (
            f'👥 Реферальная система \n\n'
            f'👤 Кол-во рефералов: {user_referrals_count} \n'
            f'💰 Заработано: {earned_amount} \n\n'
            f'— За каждую победу Вашего реферала - Вы будете получать {percent_to_referrer * 100}% \n'
            f'— Вывод заработанных денег возможен от 300 ₽ \n\n'
            f'🔗 Ваша партнёрская ссылка: \n<code>https://t.me/{bot_username}?start=ref{user_id}</code>'
        )

    @staticmethod
    async def get_information() -> str:
        users_total_count = await get_total_users_count()
        users_online_count = await users.get_users_online_count()
        games_count = await get_total_games_count()
        bets_sum = await get_total_bets_sum()

        return (
            f'♟ Информация \n\n'
            f'— Онлайн: {users_online_count} \n'
            f'— Всего игроков: {users_total_count} \n'
            f'— Сыграно игр: {games_count} \n'
            f'— Сумма ставок: {format_float_to_rub_string(bets_sum)}'
        )

    @staticmethod
    def get_information_video() -> str:
        return 'https://telegra.ph/file/f3531b3895ec78074ae0e.mp4'

    @staticmethod
    def get_top_players() -> str:
        return f'{html.bold("🎖 10-ка лучших игроков")} \n\n{html.code("Имя  |  Количество побед")}'

    @staticmethod
    async def get_profile(user: User) -> str:
        user_band = await bands.get_user_band(telegram_id=user.telegram_id)

        band_text = '— \n' if not user_band else f'<code>{user_band.title}</code> \n'
        band_text = f"🕸 Банда: {band_text}"
        rank_text = f"⚔ Твой ранг: {BandLeague.CROOKS if not user_band else user_band.league} \n"

        return (
            f'🌀 ID: {html.code(user.telegram_id)} \n'
            f'👤 Ник: {html.code(html.quote(user.name))} \n'
            f'{band_text}{rank_text}'
            f'🪙 Баланс:  {format_float_to_rub_string(user.balance)} \n'
            f'🕑 Дата регистрации: {html.code(user.registration_date.strftime("%d/%m/%Y"))} \n\n'
            f'➕ Пополнил:  {format_float_to_rub_string(await transactions.get_user_all_deposits_sum(user))} \n'
            f'➖ Вывел:  {format_float_to_rub_string(await transactions.get_user_all_withdraws_sum(user))} \n'
        )
