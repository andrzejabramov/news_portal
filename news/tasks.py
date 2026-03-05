import logging
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def send_new_post_notifications(post_id):
    """
    Асинхронная отправка уведомлений о новом посте подписчикам категорий
    """
    from news.models import Post, UserCategorySubscription
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        post = Post.objects.select_related('author__user').prefetch_related('categories').get(pk=post_id)
    except Post.DoesNotExist:
        logger.error(f"Post {post_id} not found")
        return

    # Собираем всех подписчиков на категории этого поста
    category_ids = post.categories.values_list('id', flat=True)
    subscriptions = UserCategorySubscription.objects.filter(
        category_id__in=category_ids,
        is_active=True
    ).select_related('user').distinct('user')

    # Множество для уникальных пользователей
    users = set()
    for sub in subscriptions:
        users.add(sub.user)

    if not users:
        logger.info(f"No subscribers for post {post_id}")
        return

    # Тема письма
    subject = f"Новый пост: {post.title}"

    # Контекст для шаблона
    context = {
        'post': post,
        'author': post.author.user.username,
        'categories': post.categories.all(),
        'site_url': settings.SITE_URL,
    }

    # Рендерим HTML и текстовую версию
    html_message = render_to_string('emails/new_post_notification.html', context)
    plain_message = strip_tags(html_message)

    # Собираем email'ы
    recipient_list = [user.email for user in users if user.email]

    if not recipient_list:
        logger.info(f"No valid emails for post {post_id}")
        return

    # Отправляем письма
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Sent {len(recipient_list)} notifications for post {post_id}")
    except Exception as e:
        logger.error(f"Failed to send notifications for post {post_id}: {e}")
        raise  # Повторная попытка Celery


@shared_task
def send_weekly_digest():
    """
    Асинхронная отправка еженедельного дайджеста
    """
    from news.models import Post, UserCategorySubscription
    from django.contrib.auth import get_user_model
    from collections import defaultdict

    User = get_user_model()

    # Посты за последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(
        created_at__gte=week_ago
    ).select_related('author__user').prefetch_related('categories')

    if not recent_posts.exists():
        logger.info("No recent posts for digest")
        return

    # Группируем посты по категориям
    posts_by_category = defaultdict(list)
    for post in recent_posts:
        for category in post.categories.all():
            posts_by_category[category].append(post)

    # Собираем всех активных подписчиков
    subscriptions = UserCategorySubscription.objects.filter(
        is_active=True
    ).select_related('user', 'category')

    # Группируем подписки по пользователям
    user_categories = defaultdict(set)
    for sub in subscriptions:
        if sub.user.email:  # Только с email
            user_categories[sub.user].add(sub.category)

    if not user_categories:
        logger.info("No subscribers for digest")
        return

    # Отправляем персонализированные дайджесты
    sent_count = 0
    for user, categories in user_categories.items():
        # Выбираем посты только из категорий пользователя
        user_posts_by_category = {}
        for category, posts in posts_by_category.items():
            if category in categories:
                user_posts_by_category[category] = posts

        if not user_posts_by_category:
            continue

        context = {
            'user': user,
            'posts_by_category': user_posts_by_category,
            'week_ago': week_ago,
            'site_url': settings.SITE_URL,
        }

        html_message = render_to_string('emails/weekly_digest.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=f"Еженедельный дайджест News Portal",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send digest to {user.email}: {e}")

    logger.info(f"Sent {sent_count} weekly digests")
    return sent_count


# Добавь после всех импортов, но внутри файла
@shared_task
def debug_task():
    """
    Простая задача для тестирования Celery
    """
    import time
    from datetime import datetime

    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"🐍 Debug task executed at {current_time}")
    return f"Task completed at {current_time}"