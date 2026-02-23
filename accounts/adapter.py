# accounts/adapter.py
import logging
import json
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Адаптер для кастомной валидации регистрации с русскими ошибками.
    Совместим с allauth 65.x+ (использует **kwargs).
    """

    def clean_email(self, email, **kwargs):
        """Валидация email при регистрации"""
        email = super().clean_email(email, **kwargs)
        if not email:
            raise ValidationError('❌ Введите адрес электронной почты')
        # Проверка на уникальность
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('❌ Пользователь с таким email уже зарегистрирован')
        return email

    def clean_username(self, username, **kwargs):
        """Валидация имени пользователя"""
        username = super().clean_username(username, **kwargs)
        if not username:
            raise ValidationError('❌ Введите имя пользователя')
        if len(username) < 3:
            raise ValidationError('❌ Имя пользователя должно быть не короче 3 символов')
        # Проверка на уникальность
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('❌ Пользователь с таким именем уже существует')
        return username

    def clean_password(self, password, **kwargs):
        """Валидация пароля"""
        password = super().clean_password(password, **kwargs)
        if not password:
            raise ValidationError('❌ Введите пароль')
        if len(password) < 8:
            raise ValidationError('❌ Пароль должен содержать минимум 8 символов')
        return password


class AutoConnectSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Авто-привязка Yandex OAuth к существующему пользователю по email или login.
    """

    def pre_social_login(self, request, sociallogin):
        # === ПОЛНЫЙ ЛОГ ОТВЕТА YANDEX ===
        if sociallogin.account and sociallogin.account.extra_data:  # ← ← ← ИСПРАВЛЕНО: extra_data
            logger.debug(
                f"🔍 YANDEX extra_data: {json.dumps(sociallogin.account.extra_data, ensure_ascii=False, indent=2)}")

        # Если уже привязан — выходим
        if sociallogin.is_existing:
            return

        # === Пробуем найти email во всех возможных полях ===
        email = None
        if sociallogin.account and sociallogin.account.extra_data:  # ← ← ← ИСПРАВЛЕНО: extra_data
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