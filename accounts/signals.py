## accounts/signals.py

from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from news.models import Author

# ← Импорт функции отправки письма
from news.utils.email import send_welcome_email

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

        # 2. Создаём профиль Author (если ещё нет)
        Author.objects.get_or_create(user=instance)

        # 3. Отправляем приветственное письмо (безопасно, не ломает регистрацию)
        send_welcome_email(instance)