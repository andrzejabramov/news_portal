# news/utils/email.py

import logging
from datetime import datetime
from collections import defaultdict
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from collections import defaultdict
from news.models import Post, UserCategorySubscription
from datetime import timedelta
from django.db.models import Prefetch

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

    # Определяем URL сайта (приоритет: settings.SITE_URL > Site framework > localhost)
    site_url = getattr(settings, 'SITE_URL', None)

    if not site_url:
        try:
            site = Site.objects.get_current()
            site_url = f"https://{site.domain}"
        except Exception as e:
            logger.warning(f"Site configuration error, using fallback URL: {e}")
            site_url = 'http://localhost:8000' # запасной вариант для разработки

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

    # Определяем URL сайта (приоритет: settings.SITE_URL > Site framework > localhost)
    site_url = getattr(settings, 'SITE_URL', None)

    if not site_url:
        try:
            site = Site.objects.get_current()
            site_url = f"https://{site.domain}"
        except Exception as e:
            logger.warning(f"Site configuration error, using fallback URL: {e}")
            site_url = 'http://localhost:8000'  # запасной вариант для разработки

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

            # HTML-контент (стили как в приветственном письме)
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333333; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; }}
        .header {{ background: #4CAF50; color: white; padding: 30px 20px; text-align: center; }}
        .header h2 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 30px 20px; background: #f5f5f5; }}
        .content-box {{ background: white; padding: 25px; border-radius: 5px; border: 1px solid #dddddd; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; font-weight: bold; }}
        .button:hover {{ background: #45a049; }}
        .post-preview {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; font-style: italic; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666666; background: #f5f5f5; border-top: 1px solid #dddddd; }}
        .unsubscribe-link {{ color: #f44336; text-decoration: none; }}
        .unsubscribe-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📰 Новая публикация!</h2>
        </div>
        <div class="content">
            <div class="content-box">
                <p>Здравствуйте, <strong>{user.username}</strong>!</p>

                <p>В категории <strong>«{subscription.category.name}»</strong>, на которую вы подписаны, появилась новая публикация:</p>

                <div class="post-preview">
                    <h3 style="margin: 0 0 10px 0; color: #333;">{post.title}</h3>
                    <p style="margin: 0; color: #666;">{preview_text}</p>
                </div>

                <p style="text-align: center;">
                    <a href="{post_url}" class="button">📖 Читать полностью →</a>
                </p>

                <p style="margin-top: 25px; font-size: 14px; color: #666666;">
                    Это письмо отправлено автоматически, потому что вы подписаны на категорию «{subscription.category.name}».
                </p>

                <p style="font-size: 12px; text-align: center;">
                    <a href="{site_url}/accounts/unsubscribe/?category_id={subscription.category.pk}" class="unsubscribe-link">🔕 Отписаться от уведомлений этой категории</a>
                </p>
            </div>
        </div>
        <div class="footer">
            <p>&copy; {timezone.now().year} {context['site_name']}. Все права защищены.</p>
            <p style="margin-top: 10px; font-size: 11px;">
                <a href="{site_url}" style="color: #666666; text-decoration: none;">{site_url}</a>
            </p>
        </div>
    </div>
</body>
</html>"""

            # Text-версия
            text_content = f"""Новая публикация в категории «{subscription.category.name}»

Здравствуйте, {user.username}!

В категории «{subscription.category.name}», на которую вы подписаны, появилась новая публикация:

{post.title}
{preview_text}

Читать полностью: {post_url}

---
Вы получили это письмо, потому что подписаны на категорию «{subscription.category.name}».
Отписаться: {site_url}/accounts/unsubscribe/?category_id={subscription.category.pk}

© {timezone.now().year} {context['site_name']}
"""

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

    logger.info("📰 Starting weekly digest job...")

    # Период: последние 7 дней
    week_ago = timezone.now() - timedelta(days=7)

    # Собираем статистику
    stats = {'users_processed': 0, 'emails_sent': 0, 'errors': 0}

    # Определяем URL сайта (приоритет: settings.SITE_URL > Site framework > localhost)
    site_url = getattr(settings, 'SITE_URL', None)

    if not site_url:
        try:
            site = Site.objects.get_current()
            site_url = f"https://{site.domain}"
        except Exception as e:
            logger.warning(f"Site configuration error, using fallback URL: {e}")
            site_url = 'http://localhost:8000'  # запасной вариант для разработки

    # Получаем все активные подписки с пользователями и категориями
    subscriptions = UserCategorySubscription.objects.filter(
        is_active=True
    ).select_related('user', 'category').distinct()

    # Группируем подписки по пользователям
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
            html_parts = [f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333333; margin: 0; padding: 0; }}
                    .container {{ max-width: 700px; margin: 0 auto; background: #ffffff; }}
                    .header {{ background: #4CAF50; color: white; padding: 30px 20px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .header p {{ margin: 10px 0 0; opacity: 0.9; }}
                    .content {{ padding: 30px 20px; background: #f5f5f5; }}
                    .content-box {{ background: white; padding: 25px; border-radius: 5px; border: 1px solid #dddddd; }}
                    .category-block {{ margin: 30px 0 20px; }}
                    .category-title {{ color: #4CAF50; font-size: 20px; margin: 0 0 15px; padding-bottom: 5px; border-bottom: 2px solid #4CAF50; }}
                    .post-item {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; border-left: 4px solid #4CAF50; }}
                    .post-title {{ font-size: 18px; font-weight: bold; margin: 0 0 8px; }}
                    .post-title a {{ color: #333; text-decoration: none; }}
                    .post-title a:hover {{ color: #4CAF50; text-decoration: underline; }}
                    .post-meta {{ font-size: 13px; color: #666; margin: 5px 0; }}
                    .post-preview {{ margin: 10px 0; color: #555; }}
                    .button {{ display: inline-block; padding: 8px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }}
                    .button:hover {{ background: #45a049; }}
                    .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666666; background: #f5f5f5; border-top: 1px solid #dddddd; }}
                    .stats {{ background: #e8f5e9; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }}
                    .stats-number {{ font-size: 32px; font-weight: bold; color: #4CAF50; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📰 Еженедельный дайджест</h1>
                        <p>{timezone.now().strftime('%d %B %Y')}</p>
                    </div>
                    <div class="content">
                        <div class="content-box">
                            <p>Здравствуйте, <strong>{user.username}</strong>!</p>

                            <div class="stats">
                                <span class="stats-number">{recent_posts.count()}</span>
                                <p style="margin: 5px 0 0; font-size: 16px;">новых публикаций за неделю</p>
                            </div>

                            <p>За прошедшую неделю в ваших подписках появились новые статьи:</p>"""]

            for category, posts in posts_by_category.items():
                html_parts.append(f'''
                            <div class="category-block">
                                <h2 class="category-title">📁 {category.name}</h2>''')

                for post in posts:
                    preview = post.preview() if hasattr(post, 'preview') else post.text[:124] + '...'
                    post_url = f"{site_url}/news/{post.pk}/"

                    html_parts.append(f'''
                                <div class="post-item">
                                    <div class="post-title"><a href="{post_url}">{post.title}</a></div>
                                    <div class="post-meta">
                                        {post.created_at.strftime("%d.%m.%Y")} • Автор: {post.author.user.username}
                                    </div>
                                    <div class="post-preview">{preview}</div>
                                    <a href="{post_url}" class="button">📖 Читать статью →</a>
                                </div>''')

                html_parts.append('                </div>')

            html_parts.append(f'''
                            <p style="margin: 30px 0 10px; font-size: 14px; color: #666;">
                                Вы получили это письмо, потому что подписаны на категории: 
                                <strong>{', '.join(c.name for c in categories)}</strong>
                            </p>

                            <p style="font-size: 13px; text-align: center; margin-top: 25px;">
                                <a href="{site_url}/accounts/unsubscribe/" style="color: #f44336; text-decoration: none;">🔕 Управление подписками</a> •
                                <a href="{site_url}" style="color: #666; text-decoration: none;">{site_url}</a>
                            </p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>&copy; {timezone.now().year} News Portal. Все права защищены.</p>
                        <p style="margin-top: 10px; font-size: 11px;">
                            Письмо сформировано автоматически. Пожалуйста, не отвечайте на него.
                        </p>
                    </div>
                </div>
            </body>
            </html>''')

            html_content = ''.join(html_parts)

            # Text-версия (упрощённая, но с полным списком)
            text_lines = [
                f"Еженедельный дайджест — {timezone.now().strftime('%d.%m.%Y')}",
                f"",
                f"Здравствуйте, {user.username}!",
                f"",
                f"За прошедшую неделю в ваших подписках появилось {recent_posts.count()} новых публикаций:",
                f""
            ]

            for category, posts in posts_by_category.items():
                text_lines.append(f"📁 {category.name}:")
                text_lines.append("")

                for post in posts:
                    preview = post.preview() if hasattr(post, 'preview') else post.text[:124] + '...'
                    post_url = f"{site_url}/news/{post.pk}/"
                    text_lines.append(f"  • {post.title}")
                    text_lines.append(f"    Автор: {post.author.user.username}")
                    text_lines.append(f"    Дата: {post.created_at.strftime('%d.%m.%Y')}")
                    text_lines.append(f"    {preview}")
                    text_lines.append(f"    {post_url}")
                    text_lines.append("")

                text_lines.append("")

            text_lines.append("---")
            text_lines.append(
                f"Вы получили это письмо, потому что подписаны на категории: {', '.join(c.name for c in categories)}")
            text_lines.append(f"Управление подписками: {site_url}/accounts/unsubscribe/")
            text_lines.append(f"News Portal: {site_url}")

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