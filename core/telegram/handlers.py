"""
Обработчики команд Telegram-бота.
"""
import os

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработка команды /start."""
    import django
    django.setup()

    from django.contrib.auth.models import User
    from core.models import UserProfile, TelegramLinkToken

    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer('Ошибка.')
        return

    # Проверка: уже привязан?
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        await message.answer('Аккаунт уже привязан.')
        return
    except UserProfile.DoesNotExist:
        pass

    # /start <token>
    args = message.text.split(maxsplit=1)
    token = args[1] if len(args) > 1 else None

    if not token:
        await message.answer(
            'Сначала зарегистрируйтесь на сайте. '
            'Получите ссылку для привязки в личном кабинете и нажмите /start <код>.'
        )
        return

    try:
        link_token = TelegramLinkToken.objects.get(token=token)
    except TelegramLinkToken.DoesNotExist:
        await message.answer('Ссылка недействительна. Сначала зарегистрируйтесь на сайте.')
        return

    user = link_token.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.telegram_id = telegram_id
    profile.save()
    link_token.delete()

    await message.answer('Аккаунт привязан.')
