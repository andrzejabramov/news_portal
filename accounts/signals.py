from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from news.models import Author

# ← Импорт синхронной функции (оставляем для обратной совместимости)
from news.utils.email import send_welcome_email
# ← Импорт Celery задачи
from accounts.tasks import send_welcome_email as send_welcome_email_task

import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def add_to_common_group(sender, instance, created, **kwargs):
    """
    Автоматически добавляет нового пользователя в группу common,
    создаёт профиль Author и отправляет приветственное письмо.
    """
    if created:
        # 1. Добавляем в группу common
        common_group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(common_group)
        logger.info(f"User {instance.username} added to common group")

        # 2. Создаём профиль Author (если ещё нет)
        author, created = Author.objects.get_or_create(user=instance)
        if created:
            logger.info(f"Author profile created for {instance.username}")

        # 3. Отправляем приветственное письмо (асинхронно через Celery)
        if instance.email:
            # Асинхронная отправка через Celery
            send_welcome_email_task.delay(instance.pk)
            logger.info(f"Welcome email task queued for {instance.email}")
        else:
            # Если email нет, пробуем синхронно? Но лучше залогировать
            logger.info(f"User {instance.username} has no email, skipping welcome email")

            # Опционально: можно оставить синхронную версию как fallback
            # send_welcome_email(instance)