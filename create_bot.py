from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
from aiogram.bot.api import TelegramAPIServer

load_dotenv()
storage = MemoryStorage()

# local_server = TelegramAPIServer.from_base('http://localhost:8081')
# bot = Bot(token=os.getenv('TOKEN'), server=local_server)

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)





