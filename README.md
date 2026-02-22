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

## Telegram-бот

1. Создайте бота через [@BotFather](https://t.me/BotFather) и получите токен.
2. Установите переменные окружения:
   - `TELEGRAM_BOT_TOKEN` — токен бота
   - `TELEGRAM_BOT_USERNAME` — имя бота (опционально, для ссылки привязки)
3. Запуск бота:
   ```bash
   python manage.py runbot
   ```
4. Привязка: зарегистрируйтесь на сайте, перейдите в раздел «Telegram», получите ссылку и нажмите её. В боте нажмите /start.
