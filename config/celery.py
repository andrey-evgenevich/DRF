from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра объекта Celery
app = Celery("config")

# Загрузка настроек из файла Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач
app.autodiscover_tasks()

# Настройка временной зоны
app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = settings.USE_TZ

# Импорт расписания
app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
