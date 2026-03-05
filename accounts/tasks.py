import logging
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email(user_id):
    """
    Асинхронная отправка приветственного письма новому пользователю
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return

    if not user.email:
        logger.info(f"User {user.username} has no email, skipping welcome email")
        return

    # Контекст для шаблона
    context = {
        'user': user,
        'site_url': settings.SITE_URL,
    }

    # Рендерим оба формата
    html_message = render_to_string('emails/welcome.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject='Добро пожаловать на News Portal!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        raise