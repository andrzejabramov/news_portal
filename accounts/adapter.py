# accounts/adapter.py
import logging
import json
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class AutoConnectSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # === ПОЛНЫЙ ЛОГ ОТВЕТА YANDEX ===
        if sociallogin.account and sociallogin.account.extra_data:
            logger.debug(
                f"🔍 YANDEX extra_data: {json.dumps(sociallogin.account.extra_data, ensure_ascii=False, indent=2)}")

        # Если уже привязан — выходим
        if sociallogin.is_existing:
            return

        # === Пробуем найти email во всех возможных полях ===
        email = None
        if sociallogin.account and sociallogin.account.extra_data:
            data = sociallogin.account.extra_data
            # Стандартные поля
            email = data.get('email') or data.get('default_email')
            # Если email в списке
            if not email and isinstance(data.get('emails'), list) and data['emails']:
                email = data['emails'][0]
            # Если вложенный объект
            if not email and isinstance(data.get('default_email'), dict):
                email = data['default_email'].get('value')

        # === Если email не нашли — пробуем по login (username) ===
        if not email:
            login = sociallogin.account.extra_data.get('login') if sociallogin.account else None
            if login:
                logger.debug(f"🔍 Пробуем найти пользователя по login: {login}")
                User = get_user_model()
                try:
                    user = User.objects.get(username__iexact=login)
                    logger.debug(f"✅ Нашли пользователя: {user.username}")
                    sociallogin.connect(request, user)
                    return
                except User.DoesNotExist:
                    logger.debug(f"⚠️ Пользователь с login={login} не найден")
            logger.debug("❌ Email и login не найдены или пользователь не найден")
            return

        logger.debug(f"✅ Нашли email: {email}")

        # === Привязываем по email ===
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)
            logger.debug(f"✅ Connected {sociallogin.account.provider} to {user.username}")
        except User.DoesNotExist:
            logger.debug(f"⚠️ No user with email {email}")