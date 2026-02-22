"""
Запуск Telegram-бота.
"""
import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand

from core.telegram.bot import bot, dp


class Command(BaseCommand):
    help = 'Запуск Telegram-бота (polling)'

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write('Установите переменную окружения TELEGRAM_BOT_TOKEN')
            return

        async def main():
            await dp.start_polling(bot)

        asyncio.run(main())
