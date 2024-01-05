from typing import Generator, Any

import aiohttp
import json

from settings import Config


url = 'https://pay.crypt.bot/api'

headers = {
    "Host": "pay.crypt.bot",
    "Crypto-Pay-API-Token": Config.Payments.CRYPTO_BOT_TOKEN
}


async def _make_get_request(method: str, params: dict = None) -> list[dict] | None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/{method}", headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('result')
            else:
                print(f"Error: {response.status}")
                return None


async def _make_put_request(method: str, data: dict) -> list[dict] | None:
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{url}/{method}", headers=headers, data=data) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('result')
            else:
                return None


async def get_currencies() -> Generator | None:
    response_data = await _make_get_request('getCurrencies')
    if response_data:
        return (currency.get('code') for currency in response_data[:8])


async def create_invoice(
        currency_code: str,
        amount: float | str,
        user_id: int,
        bot_username: str
) -> dict | None:

    data = {
        'asset': currency_code,
        'amount': str(amount),
        'description': f'Пополнение баланса в боте @{bot_username}',
        'hidden_message': '✅ Готово! Теперь вернитесь в бота и нажмите "Проверить"',
        'payload': str(user_id),
        'paid_btn_name': 'callback',
        'paid_btn_url': f'https://t.me/{bot_username}',
        'allow_comments': False,
        'allow_anonymous': False,
        'expires_in': 3600
    }

    return await _make_put_request('createInvoice', data)


async def get_exchange_rate(source_currency: str, target_currency: str = 'RUB') -> float:
    response = await _make_get_request('getExchangeRates')
    for item in response:
        if item.get('source') == source_currency and item.get('target') == target_currency:
            return float(item.get('rate'))


async def get_invoice(invoice_id: int) -> dict:
    params = {
        'invoice_ids': invoice_id,
        'count': 1
    }
    invoice = await _make_get_request('getInvoices', params=params)
    return invoice.get('items')[0]
