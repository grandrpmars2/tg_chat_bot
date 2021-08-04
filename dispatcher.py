from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot
from filters import IsAdminFilter, IsOwnerFilter
import config

bot = Bot(config.BOT_TOKEN, parse_mode = 'HTML')
dp = Dispatcher(bot, storage = MemoryStorage())

dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(IsOwnerFilter)