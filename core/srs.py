"""
Алгоритм интервального повторения SM-2.
"""
from datetime import date, timedelta


def update_schedule(schedule, quality):
    """
    Обновляет расписание по алгоритму SM-2.

    quality — целое число от 0 до 5 (оценка recall).
    """
    today = date.today()

    # Обновление easiness_factor по формуле SM-2
    ef = schedule.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    schedule.easiness_factor = max(1.3, round(ef, 2))

    if quality < 3:
        schedule.repetition = 0
        schedule.interval = 1
    else:
        schedule.repetition += 1
        if schedule.repetition == 1:
            schedule.interval = 1
        elif schedule.repetition == 2:
            schedule.interval = 6
        else:
            schedule.interval = round(schedule.interval * schedule.easiness_factor)

    schedule.next_review = today + timedelta(days=schedule.interval)
    schedule.last_reviewed = today
    schedule.save()
