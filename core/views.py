from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Card
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
            return redirect('card_list')
    else:
        form = CardForm(instance=card)
    return render(request, 'core/card_form.html', {'form': form, 'title': 'Редактирование карточки'})


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
    today = date.today()
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
            update_schedule(card.schedule, int(quality))
            return redirect('review_today')

        return redirect(f"{reverse('review_today')}?card={card_id}&revealed=1")

    card_id = request.GET.get('card')
    revealed = request.GET.get('revealed')

    if card_id:
        card = get_object_or_404(Card, pk=card_id, user=request.user)
        if card not in cards:
            card = cards.first()
    else:
        card = cards.first()

    return render(request, 'core/review.html', {
        'card': card,
        'revealed': revealed,
    })
