from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties

from web.core import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode='HTMl'),
)
dp = Dispatcher()