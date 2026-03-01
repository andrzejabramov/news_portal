# accounts/adapter.py
import logging
import json
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class AutoConnectSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Авто-привязка Yandex OAuth к существующему пользователю по email.
    """

    def pre_social_login(self, request, sociallogin):
        # Если уже привязан — выходим
        if sociallogin.is_existing:
            return

        # Пробуем найти email
        email = None
        if sociallogin.account and sociallogin.account.extra_data:
            data = sociallogin.account.extra_data
            email = data.get('email') or data.get('default_email')
            if not email and isinstance(data.get('emails'), list) and data['emails']:
                email = data['emails'][0]

        if not email:
            return  # Нет email — создастся новый пользователь

        # Привязываем к существующему пользователю
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)
            logger.debug(f"✅ Connected Yandex to {user.username}")
        except User.DoesNotExist:
            pass  # Создастся новый пользователь