"""
Обработчики команд Telegram-бота.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

router = Router()

HELP_TEXT = """Доступные команды:

/progress — ваша статистика
/cards — список карточек
/today — слова на сегодня
/test — пройти тест
/say слово — озвучить слово
/help — список команд"""


@router.message(Command('say'))
async def cmd_say(message: Message) -> None:
    """Обработка команды /say."""
    import django
    django.setup()

    import tempfile
    from pathlib import Path

    from core.models import UserProfile

    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer('Ошибка.')
        return

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await message.answer('Аккаунт не привязан. Сначала зарегистрируйтесь на сайте.')
        return

    args = message.text.split(maxsplit=1)
    word = args[1].strip() if len(args) > 1 else ''
    if not word:
        await message.answer('Использование: /say слово')
        return

    try:
        from gtts import gTTS

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            path = Path(f.name)
        try:
            gTTS(text=word, lang='en').save(path)
            await message.answer_voice(voice=FSInputFile(path))
        finally:
            if path.exists():
                path.unlink()
    except Exception:
        await message.answer('Не удалось сгенерировать озвучку.')


@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    """Обработка команды /help."""
    await message.answer(HELP_TEXT)


def _get_today_cards(profile):
    """Карточки на сегодня для пользователя."""
    from django.utils import timezone
    from core.models import Card

    today = timezone.now().date()
    return Card.objects.filter(
        user=profile.user,
        schedule__next_review__lte=today,
    ).order_by('schedule__next_review')


def _show_card_word(card):
    """Клавиатура: Показать перевод."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Показать перевод', callback_data=f'show_{card.pk}')]
    ])


def _show_card_rating(card):
    """Клавиатура: кнопки 0-5."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=str(i), callback_data=f'rate_{card.pk}_{i}')
            for i in range(6)
        ]
    ])


@router.message(Command('test'))
async def cmd_test(message: Message) -> None:
    """Обработка команды /test."""
    import django
    django.setup()

    from core.models import UserProfile

    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer('Ошибка.')
        return

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await message.answer('Аккаунт не привязан. Сначала зарегистрируйтесь на сайте.')
        return

    cards = _get_today_cards(profile)
    if not cards:
        await message.answer('На сегодня нет слов для тестирования.')
        return

    card = cards.first()
    await message.answer(card.word, reply_markup=_show_card_word(card))


@router.callback_query(F.data.startswith('show_'))
async def callback_show(callback: CallbackQuery) -> None:
    """Показать перевод карточки."""
    import django
    django.setup()

    from core.models import Card, UserProfile

    telegram_id = callback.from_user.id if callback.from_user else None
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await callback.answer('Аккаунт не привязан.')
        return

    card_id = int(callback.data.split('_')[1])
    try:
        card = Card.objects.get(pk=card_id, user=profile.user)
    except Card.DoesNotExist:
        await callback.answer('Карточка не найдена.')
        return

    text = f'{card.word}\n\n{card.translation}'
    await callback.message.edit_text(text, reply_markup=_show_card_rating(card))
    await callback.answer()


@router.callback_query(F.data.startswith('rate_'))
async def callback_rate(callback: CallbackQuery) -> None:
    """Оценка карточки и переход к следующей."""
    import django
    django.setup()

    from core.models import Card, UserProfile, ReviewLog
    from core.srs import update_schedule

    telegram_id = callback.from_user.id if callback.from_user else None
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        await callback.answer('Аккаунт не привязан.')
        return

    parts = callback.data.split('_')
    card_id = int(parts[1])
    quality = int(parts[2])

    try:
        card = Card.objects.get(pk=card_id, user=profile.user)
    except Card.DoesNotExist:
        await callback.answer('Карточка не найдена.')
        return

    await callback.message.delete_reply_markup()

    ReviewLog.objects.create(
        card=card,
        user=profile.user,
        quality=quality,
        is_correct=quality >= 3,
    )
    update_schedule(card.schedule, quality)

    cards = _get_today_cards(profile)
    if not cards:
        await callback.message.edit_text('Тест завершён. На сегодня слов больше нет.')
    else:
        card = cards.first()
        await callback.message.edit_text(card.word, reply_markup=_show_card_word(card))

    await callback.answer()


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
