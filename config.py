from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import Database

bot = Bot("5871658812:AAHacjlJea1BlQRPH88PONSqkzmb6KhrPAg")
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database("dbase")
