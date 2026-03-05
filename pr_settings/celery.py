import os
from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pr_settings.settings')

app = Celery('newsPortal')

# Используем строку конфигурации из настроек Django с префиксом CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
