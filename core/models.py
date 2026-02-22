from datetime import date

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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Schedule.objects.create(
                card=self,
                repetition=0,
                interval=0,
                easiness_factor=2.5,
                next_review=date.today(),
            )


class Schedule(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE)
    repetition = models.IntegerField(default=0)
    interval = models.IntegerField(default=0)
    easiness_factor = models.FloatField(default=2.5)
    next_review = models.DateField()
    last_reviewed = models.DateField(null=True, blank=True)
