import asyncio
import logging
import colorama as colorama
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *
from database import DataBase
from aiogram.client.default import DefaultBotProperties
from aiocryptopay import AioCryptoPay, Networks

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)
colorama.init()

bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
db = DataBase('database.db')
crypto = AioCryptoPay(token=api_cryptobot, network=Networks.MAIN_NET)
scheduler = AsyncIOScheduler()
admin = Router()
lock = asyncio.Lock()
