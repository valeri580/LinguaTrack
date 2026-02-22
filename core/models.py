from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Начальный'),
        ('middle', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    example = models.TextField(blank=True)
    note = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.word
