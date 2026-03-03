## news/signals.py

import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from news.models import Post, UserCategorySubscription
from news.utils.email import send_new_post_notification

logger = logging.getLogger(__name__)


def _send_notification_if_ready(post):
    """
    Внутренняя функция отправки уведомлений.
    Вызывается из разных сигналов (post_save, m2m_changed).
    """
    try:
        # Получаем все категории этого поста
        post_categories = post.categories.all()

        if not post_categories.exists():
            logger.debug(f"Post {post.pk} has no categories yet")
            return

        # Находим всех активных подписчиков этих категорий
        subscribers = UserCategorySubscription.objects.filter(
            category__in=post_categories,
            is_active=True,
        ).select_related('user', 'category').distinct()

        if not subscribers.exists():
            logger.debug(f"No active subscribers for post {post.pk} categories")
            return

        # Отправляем уведомления
        result = send_new_post_notification(post, subscribers)

        logger.info(
            f"Notifications for post '{post.title}': "
            f"sent={result['sent']}, failed={result['failed']}"
        )

    except Exception as e:
        logger.error(f"Failed to send post notifications: {type(e).__name__}: {e}", exc_info=True)


@receiver(post_save, sender=Post)
def notify_on_post_create(sender, instance, created, **kwargs):
    """
    Срабатывает при создании поста.
    Пытается отправить уведомления (если категории уже есть).
    """
    if created:
        logger.info(f"Post created: {instance.title} (pk={instance.pk})")
        _send_notification_if_ready(instance)


@receiver(m2m_changed, sender=Post.categories.through)
def notify_on_category_change(sender, instance, action, **kwargs):
    """
    Срабатывает при изменении категорий поста.

    action: 'post_add', 'post_remove', 'post_clear', 'pre_add', etc.
    """
    # Отправляем уведомление только когда категории ДОБАВЛЯЮТСЯ
    if action == 'post_add':
        logger.info(f"Categories added to post: {instance.title} (pk={instance.pk})")

        # Защита: не отправляем, если пост создан давно (чтобы не спамить при редактировании)
        from django.utils import timezone
        from datetime import timedelta

        if timezone.now() - instance.created_at < timedelta(minutes=30):
            _send_notification_if_ready(instance)
        else:
            logger.debug(f"Post {instance.pk} is older than 30 minutes, skipping notification")