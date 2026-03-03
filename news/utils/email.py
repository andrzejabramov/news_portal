# news/utils/email.py

import logging
from datetime import datetime
from collections import defaultdict

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from news.models import Post, UserCategorySubscription


logger = logging.getLogger(__name__)


# =============================================================================
# ПРИВЕТСТВЕННОЕ ПИСЬМО (при регистрации пользователя)
# =============================================================================

def send_welcome_email(user):
    """
    Отправляет приветственное письмо новому пользователю.

    Args:
        user: Объект пользователя Django

    Returns:
        bool: True если письмо отправлено успешно, False если произошла ошибка
    """
    if not user or not user.email:
        logger.warning(f"Cannot send welcome email: user {user} has no email")
        return False

    try:
        site = Site.objects.get_current()
        site_url = f"https://{site.domain}"
    except Exception as e:
        logger.warning(f"Site configuration error, using fallback URL: {e}")
        site_url = getattr(settings, 'DEFAULT_SITE_URL', 'http://localhost:8000')

    context = {
        'user': user,
        'site_url': site_url,
        'current_year': datetime.now().year,
    }

    try:
        html_content = render_to_string('emails/welcome.html', context)
        text_content = render_to_string('emails/welcome.txt', context)

        subject = f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')}Добро пожаловать, {user.username}!"

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@newsportal.local'),
            to=[user.email],
            reply_to=[getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@newsportal.local')],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Welcome email sent to {user.email} (user: {user.username})")
        return True

    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {type(e).__name__}: {e}", exc_info=True)
        return False


# =============================================================================
# УВЕДОМЛЕНИЕ О НОВОМ ПОСТЕ (для подписчиков категории)
# =============================================================================

def send_new_post_notification(post, subscribers):
    """
    Отправляет уведомление о новом посте подписчикам категории.

    Args:
        post: Объект Post (новость/статья)
        subscribers: QuerySet объектов UserCategorySubscription

    Returns:
        dict: {'sent': int, 'failed': int} — статистика отправки
    """
    if not subscribers.exists():
        return {'sent': 0, 'failed': 0}

    try:
        site = Site.objects.get_current()
        site_url = f"https://{site.domain}"
    except Exception as e:
        logger.warning(f"Site configuration error: {e}")
        site_url = getattr(settings, 'DEFAULT_SITE_URL', 'http://localhost:8000')

    post_url = f"{site_url}/news/{post.pk}/"

    context = {
        'post': post,
        'post_url': post_url,
        'site_name': getattr(settings, 'SITE_NAME', 'News Portal'),
    }

    sent_count = 0
    failed_count = 0

    for subscription in subscribers:
        user = subscription.user

        if not user.email:
            logger.warning(f"Skipping user {user.username}: no email")
            failed_count += 1
            continue

        try:
            subject = f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')}Новая публикация: {post.title}"
            preview_text = post.preview() if hasattr(post, 'preview') else post.text[:124] + '...'

            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .button {{ display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; }}
        .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h2>📰 Новая публикация!</h2></div>
        <div class="content">
            <p>Здравствуйте, <strong>{user.username}</strong>!</p>
            <p>В категории <strong>{subscription.category.name}</strong> появилась новая публикация:</p>
            <h3>{post.title}</h3>
            <p><em>{preview_text}</em></p>
            <p><a href="{post_url}" class="button">Читать полностью →</a></p>
            <p style="font-size: 12px; color: #666;">
                Вы получили это письмо, потому что подписаны на категорию "{subscription.category.name}".
                <br><a href="{site_url}/accounts/unsubscribe/?category_id={subscription.category.pk}">Отписаться</a>
            </p>
        </div>
        <div class="footer"><p>&copy; {context['site_name']}</p></div>
    </div>
</body>
</html>"""

            text_content = f"""Новая публикация на {context['site_name']}!

Здравствуйте, {user.username}!

В категории "{subscription.category.name}" появилась новая публикация:

{post.title}
{preview_text}

Читать полностью: {post_url}

---
Вы получили это письмо, потому что подписаны на категорию "{subscription.category.name}".
Отписаться: {site_url}/accounts/unsubscribe/?category_id={subscription.category.pk}
            """.strip()

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@newsportal.local'),
                to=[user.email],
                reply_to=[getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@newsportal.local')],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            logger.info(f"New post notification sent to {user.email} (post: {post.title})")
            sent_count += 1

        except Exception as e:
            logger.error(f"Failed to send notification to {user.email}: {type(e).__name__}: {e}", exc_info=True)
            failed_count += 1

    return {'sent': sent_count, 'failed': failed_count}


# =============================================================================
# ЕЖЕНЕДЕЛЬНЫЙ ДАЙДЖЕСТ (периодическая задача)
# =============================================================================

def send_weekly_digest():
    """
    Отправляет еженедельный дайджест подписчикам.

    Собирает все посты, опубликованные за последние 7 дней,
    группирует их по категориям и отправляет персонализированные письма
    всем активным подписчикам.

    Returns:
        dict: {'users_processed': int, 'emails_sent': int, 'errors': int}
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Prefetch

    logger.info("📰 Starting weekly digest job...")

    # Период: последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)

    # Собираем статистику
    stats = {'users_processed': 0, 'emails_sent': 0, 'errors': 0}

    try:
        site = Site.objects.get_current()
        site_url = f"https://{site.domain}"
    except Exception as e:
        logger.warning(f"Site configuration error: {e}")
        site_url = getattr(settings, 'DEFAULT_SITE_URL', 'http://localhost:8000')

    # Получаем все активные подписки с пользователями и категориями
    subscriptions = UserCategorySubscription.objects.filter(
        is_active=True
    ).select_related('user', 'category').distinct()

    # Группируем подписки по пользователям
    from collections import defaultdict
    user_subscriptions = defaultdict(list)
    for sub in subscriptions:
        if sub.user.email:  # только пользователи с email
            user_subscriptions[sub.user].append(sub.category)

    logger.info(f"Found {len(user_subscriptions)} users with active subscriptions")

    # Для каждого пользователя формируем персональный дайджест
    for user, categories in user_subscriptions.items():
        try:
            # Находим посты в подписанных категориях за последнюю неделю
            recent_posts = Post.objects.filter(
                categories__in=categories,
                created_at__gte=week_ago,
            ).select_related('author__user').prefetch_related('categories').distinct().order_by('-created_at')

            if not recent_posts.exists():
                logger.debug(f"No new posts for user {user.username} this week")
                continue

            # Группируем посты по категориям для удобного отображения
            posts_by_category = defaultdict(list)
            for post in recent_posts:
                # Добавляем только те категории, на которые подписан пользователь
                user_cats = [c.pk for c in categories]
                for cat in post.categories.all():
                    if cat.pk in user_cats:
                        posts_by_category[cat].append(post)
                        break

            # Формируем письмо
            subject = f"{getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')}Еженедельный дайджест — {timezone.now().strftime('%d.%m.%Y')}"

            # HTML-контент
            html_parts = [f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
                body{{font-family:Arial,sans-serif;line-height:1.6;color:#333}}
                .container{{max-width:700px;margin:0 auto;padding:20px}}
                .header{{background:#4CAF50;color:white;padding:25px;text-align:center}}
                .content{{padding:25px;background:#f9f9f9}}
                .category{{margin-bottom:25px;padding:15px;background:white;border-radius:5px;border:1px solid #ddd}}
                .post{{margin:15px 0;padding:10px 0;border-bottom:1px solid #eee}}
                .post:last-child{{border-bottom:none}}
                .post-title{{font-weight:bold;color:#333;margin:5px 0}}
                .post-meta{{font-size:12px;color:#666}}
                .button{{display:inline-block;padding:10px 20px;background:#4CAF50;color:white;text-decoration:none;border-radius:4px;margin:5px 0}}
                .footer{{padding:20px;text-align:center;font-size:12px;color:#666}}
            </style></head><body><div class="container">
            <div class="header"><h1>📰 Еженедельный дайджест</h1><p>{timezone.now().strftime('%d %B %Y')}</p></div>
            <div class="content">
            <p>Здравствуйте, <strong>{user.username}</strong>!</p>
            <p>За прошедшую неделю в ваших подписках появилось <strong>{recent_posts.count()} новых публикаций</strong>:</p>"""]

            for category, posts in posts_by_category.items():
                html_parts.append(
                    f'<div class="category"><h3 style="margin:0 0 10px 0;color:#4CAF50">📁 {category.name}</h3>')
                for post in posts:
                    preview = post.preview() if hasattr(post, 'preview') else post.text[:124] + '...'
                    post_url = f"{site_url}/news/{post.pk}/"
                    html_parts.append(f'''<div class="post">
                        <div class="post-title"><a href="{post_url}" style="color:#4CAF50;text-decoration:none">{post.title}</a></div>
                        <div class="post-meta">{post.created_at.strftime("%d.%m.%Y")} • {post.author.user.username}</div>
                        <p style="margin:8px 0;font-size:14px">{preview}</p>
                        <a href="{post_url}" class="button">Читать →</a>
                    </div>''')
                html_parts.append('</div>')

            html_parts.append(f'''</div><div class="footer">
                <p>Вы получили это письмо, потому что подписаны на категории: {', '.join(c.name for c in categories)}</p>
                <p><a href="{site_url}/accounts/unsubscribe/" style="color:#666">Управление подписками</a> | 
                <a href="{site_url}" style="color:#666">News Portal</a></p>
                <p>&copy; {timezone.now().year} News Portal</p>
            </div></div></body></html>''')

            html_content = ''.join(html_parts)

            # Text-версия (упрощённая)
            text_lines = [
                f"Еженедельный дайджест — {timezone.now().strftime('%d.%m.%Y')}",
                f"\nЗдравствуйте, {user.username}!",
                f"\nЗа прошедшую неделю в ваших подписках появилось {recent_posts.count()} новых публикаций:",
                ""
            ]
            for category, posts in posts_by_category.items():
                text_lines.append(f"📁 {category.name}:")
                for post in posts:
                    preview = post.preview() if hasattr(post, 'preview') else post.text[:124] + '...'
                    post_url = f"{site_url}/news/{post.pk}/"
                    text_lines.append(f"  • {post.title} — {preview}\n    {post_url}")
                text_lines.append("")
            text_lines.append(f"\nУправление подписками: {site_url}/accounts/unsubscribe/")
            text_content = '\n'.join(text_lines)

            # Отправляем письмо
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@newsportal.local'),
                to=[user.email],
                reply_to=[getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@newsportal.local')],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            logger.info(
                f"Weekly digest sent to {user.email} ({len(posts_by_category)} categories, {recent_posts.count()} posts)")
            stats['emails_sent'] += 1

        except Exception as e:
            logger.error(f"Failed to send digest to {user.email}: {type(e).__name__}: {e}", exc_info=True)
            stats['errors'] += 1

        stats['users_processed'] += 1

    logger.info(f"✅ Weekly digest completed: {stats}")
    return stats