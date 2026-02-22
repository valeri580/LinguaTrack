"""
Telegram-бот LinguaTrack.
"""
from django.conf import settings

from aiogram import Bot, Dispatcher

from .handlers import router

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)
