# LinguaTrack

Минимальный Django-проект MVP системы изучения слов.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

Рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# или: source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

## Миграции

```bash
python manage.py migrate
```

## Создание суперпользователя

```bash
python manage.py createsuperuser
```

Следуйте инструкциям для ввода имени пользователя, email и пароля.

## Запуск сервера

```bash
python manage.py runserver
```

Приложение будет доступно по адресу: http://127.0.0.1:8000/
