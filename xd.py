import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties

# === Настройки ===
TELEGRAM_TOKEN = "7997558659:AAF-wnhcK1eV3kNT5MddW8oqb6M_fgQQiXg"
CRYPTOPAY_API_TOKEN = "385507:AAUgEwtlUl12rc80RRdZtOEX4VMd9X2EExh"
BASE_URL = "https://pay.crypt.bot/api"

headers = {
    "Crypto-Pay-API-Token": CRYPTOPAY_API_TOKEN
}

router = Router()

# === /start Handler ===
@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Отправь сумму, и я создам чек в USDT.")

# === Number Handler ===
@router.message(F.text.regexp(r"^\d+$"))
async def create_voucher(message: Message):
    amount = message.text
    data = {
        "asset": "USDT",
        "amount": amount,
        "currency": "USDT",
        "description": f"Чек от {message.from_user.full_name}"
    }

    response = requests.post(f"{BASE_URL}/createVoucher", json=data, headers=headers)
    if response.ok:
        voucher = response.json()['result']
        link = f"https://t.me/CryptoBot?start=voucher_{voucher['voucher_id']}"
        await message.answer(f"Вот твой чек: {link}")
    else:
        await message.answer("Ошибка при создании чека.")

# === Fallback: Echo Anything Else ===
@router.message()
async def echo_unknown(message: Message):
    await message.answer("Я понимаю только числа. Напиши сумму, например: 10")

# === Main Setup ===
async def main():
    print("Starting bot...")  # Debug print
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    session = AiohttpSession()
    bot = Bot(
        token=TELEGRAM_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)

# === Entry Point ===
if __name__ == "__main__":
    asyncio.run(main())
