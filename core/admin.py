from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'difficulty', 'user', 'created_at')
    list_filter = ('difficulty', 'user')
