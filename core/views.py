import os
import random
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Card, ReviewLog, TelegramLinkToken
from .forms import CardForm
from .srs import update_schedule


def home(request):
    """Главная страница."""
    return render(request, 'core/home.html')


def register(request):
    """Регистрация пользователя."""
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def card_list(request):
    """Список карточек пользователя."""
    cards = Card.objects.filter(user=request.user)
    difficulty = request.GET.get('difficulty')
    if difficulty:
        cards = cards.filter(difficulty=difficulty)
    return render(request, 'core/card_list.html', {'cards': cards})


@login_required
def card_create(request):
    """Создание карточки."""
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('card_list')
    else:
        form = CardForm()
    return render(request, 'core/card_form.html', {'form': form, 'title': 'Новая карточка'})


@login_required
def card_edit(request, pk):
    """Редактирование карточки."""
    card = get_object_or_404(Card, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            next_review = request.POST.get('next_review')
            if next_review:
                card.schedule.next_review = datetime.strptime(next_review, '%Y-%m-%d').date()
                card.schedule.save()
            return redirect('card_list')
    else:
        form = CardForm(instance=card)
    return render(request, 'core/card_form.html', {'form': form, 'title': 'Редактирование карточки', 'card': card})


@login_required
def card_delete(request, pk):
    """Удаление карточки."""
    card = get_object_or_404(Card, pk=pk, user=request.user)
    if request.method == 'POST':
        card.delete()
        return redirect('card_list')
    return render(request, 'core/card_confirm_delete.html', {'card': card})


@login_required
def review_today(request):
    """Повторение карточек на сегодня."""
    today = timezone.now().date()
    cards = Card.objects.filter(
        user=request.user,
        schedule__next_review__lte=today,
    ).order_by('schedule__next_review')

    if not cards.exists():
        return render(request, 'core/review.html', {'card': None})

    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        quality = request.POST.get('quality')

        if quality is not None:
            card = get_object_or_404(Card, pk=card_id, user=request.user)
            quality_int = int(quality)
            ReviewLog.objects.create(
                card=card,
                user=request.user,
                quality=quality_int,
                is_correct=quality_int >= 3,
            )
            update_schedule(card.schedule, quality_int)
            return redirect('review_today')

        reverse_dir = request.POST.get('reverse', '0') == '1'
        return redirect(f"{reverse('review_today')}?card={card_id}&revealed=1&reverse={'1' if reverse_dir else '0'}")

    card_id = request.GET.get('card')
    revealed = request.GET.get('revealed')
    reverse_dir = request.GET.get('reverse') == '1'

    if card_id:
        card = get_object_or_404(Card, pk=card_id, user=request.user)
        if card not in cards:
            card = cards.first()
            reverse_dir = random.choice([True, False])
    else:
        card = cards.first()
        reverse_dir = random.choice([True, False])

    return render(request, 'core/review.html', {
        'card': card,
        'revealed': revealed,
        'reverse': reverse_dir,
    })


@login_required
def telegram_link(request):
    """Генерация ссылки для привязки Telegram."""
    import secrets
    token = secrets.token_urlsafe(32)
    TelegramLinkToken.objects.create(user=request.user, token=token)
    bot_username = os.getenv('TELEGRAM_BOT_USERNAME', 'LinguaTrackBot')
    url = f'https://t.me/{bot_username}?start={token}'
    return render(request, 'core/telegram_link.html', {'link': url})


@login_required
def progress_view(request):
    """Статистика прогресса."""
    user = request.user

    total_words = Card.objects.filter(user=user).count()
    learned_words = Card.objects.filter(user=user, schedule__repetition__gte=3).count()
    total_reviews = ReviewLog.objects.filter(user=user).count()
    total_errors = ReviewLog.objects.filter(user=user, is_correct=False).count()
    success_rate = ((total_reviews - total_errors) / total_reviews * 100) if total_reviews > 0 else None

    return render(request, 'core/progress.html', {
        'total_words': total_words,
        'learned_words': learned_words,
        'total_reviews': total_reviews,
        'total_errors': total_errors,
        'success_rate': success_rate,
    })
