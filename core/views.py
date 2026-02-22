from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import Card
from .forms import CardForm


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
