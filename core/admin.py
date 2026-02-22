from django.contrib import admin
from .models import Card, ReviewLog


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'difficulty', 'user', 'created_at')
    list_filter = ('difficulty', 'user')


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ('card', 'user', 'quality', 'is_correct', 'reviewed_at')
