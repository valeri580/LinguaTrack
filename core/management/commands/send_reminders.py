"""
Отправка напоминаний о повторении слов.
"""
import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Card, UserProfile
from core.telegram.bot import bot


REMINDER_TEXT = """Пора повторить слова.
Используйте /today или /test."""


class Command(BaseCommand):
    help = 'Отправка напоминаний пользователям с карточками на сегодня'

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write('Установите переменную окружения TELEGRAM_BOT_TOKEN')
            return

        today = timezone.now().date()
        profiles = UserProfile.objects.filter(telegram_id__isnull=False)

        to_notify = []
        for profile in profiles:
            has_cards = Card.objects.filter(
                user=profile.user,
                schedule__next_review__lte=today,
            ).exists()

            if has_cards and profile.last_notification_date != today:
                to_notify.append(profile)

        if to_notify:
            asyncio.run(self._send_all(to_notify, today))

    async def _send_all(self, profiles, today):
        try:
            for profile in profiles:
                try:
                    await bot.send_message(
                        chat_id=profile.telegram_id,
                        text=REMINDER_TEXT,
                    )
                    profile.last_notification_date = today
                    profile.save()
                except Exception as e:
                    self.stderr.write(f'Ошибка отправки пользователю {profile.user.username}: {e}')
        finally:
            if hasattr(bot, 'session') and bot.session:
                await bot.session.close()
