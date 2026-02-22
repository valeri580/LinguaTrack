"""
Обработчики команд Telegram-бота.
"""
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

HELP_TEXT = """Доступные команды:

/progress — ваша статистика
/cards — список карточек
/today — слова на сегодня
/test — пройти тест
/say слово — озвучить слово
/help — список команд"""


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    """Обработка команды /help."""
    await message.answer(HELP_TEXT)


@router.message(Command('today'))
async def cmd_today(message: Message) -> None:
    """Обработка команды /today."""
    import django
    django.setup()

    from django.utils import timezone
    from core.models import Card, UserProfile

    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer('Ошибка.')
        return

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await message.answer('Аккаунт не привязан. Сначала зарегистрируйтесь на сайте.')
        return

    today = timezone.now().date()
    cards = Card.objects.filter(
        user=profile.user,
        schedule__next_review__lte=today,
    ).order_by('schedule__next_review')[:10]

    if not cards:
        await message.answer('На сегодня нет слов для повторения.')
        return

    lines = ['Слова на сегодня:']
    for i, card in enumerate(cards, 1):
        lines.append(f'{i}. {card.word} — {card.translation}')
    await message.answer('\n'.join(lines))


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработка команды /start."""
    import django
    django.setup()

    from core.models import UserProfile, TelegramLinkToken

    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer('Ошибка.')
        return

    # Проверка: уже привязан?
    args = message.text.split(maxsplit=1)
    token = args[1] if len(args) > 1 else None
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        if not token:
            await message.answer(HELP_TEXT)
        else:
            await message.answer('Аккаунт уже привязан.')
        return
    except UserProfile.DoesNotExist:
        pass

    # /start <token>
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
