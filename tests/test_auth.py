# tests/test_auth.py
import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestRegistration:
    """Тесты регистрации (стандартная форма allauth)"""

    def test_1_1_empty_email(self, client):
        """1.1: Пустой email → ошибка валидации"""
        response = client.post(reverse('account_signup'), {
            'username': 'testuser', 'email': '',
            'password1': 'TestPass123', 'password2': 'TestPass123'
        })
        assert response.status_code == 200
        content = response.content.decode().lower()
        # Стандартная ошибка allauth/Django
        assert 'required' in content or 'обязатель' in content

    def test_1_2_email_already_exists(self, client, user_common):
        """1.2: Email уже занят → ошибка"""
        response = client.post(reverse('account_signup'), {
            'username': 'testuser2', 'email': 'common@test.com',
            'password1': 'TestPass123', 'password2': 'TestPass123'
        })
        assert response.status_code == 200
        content = response.content.decode().lower()
        # Стандартная ошибка allauth
        assert 'already' in content or 'уже' in content or 'exists' in content

    def test_1_4_empty_username(self, client):
        """1.4: Пустой username → ошибка"""
        response = client.post(reverse('account_signup'), {
            'username': '', 'email': 'test@example.com',
            'password1': 'TestPass123', 'password2': 'TestPass123'
        })
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert 'required' in content or 'обязатель' in content

    def test_1_8_password_too_short(self, client):
        """1.8: Пароль короче 8 символов → ошибка Django validator"""
        response = client.post(reverse('account_signup'), {
            'username': 'testuser', 'email': 'test@example.com',
            'password1': 'short', 'password2': 'short'
        })
        assert response.status_code == 200
        content = response.content.decode().lower()
        # Django PasswordValidator или allauth
        assert 'short' in content or '8' in content or 'корот' in content

    def test_1_11_successful_registration(self, client):
        """1.11: Успешная регистрация → редирект + пользователь в common"""
        response = client.post(reverse('account_signup'), {
            'username': 'newuser', 'email': 'newuser@test.com',
            'password1': 'TestPass123', 'password2': 'TestPass123'
        })
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()
        user = User.objects.get(username='newuser')
        assert user.groups.filter(name='common').exists()


@pytest.mark.django_db
class TestLogin:
    """Тесты входа"""

    def test_2_2_nonexistent_user(self, client):
        """2.2: Несуществующий пользователь → ошибка"""
        response = client.post(reverse('account_login'), {
            'login': 'fakeuser', 'password': 'FakePass123'
        })
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert 'incorrect' in content or 'неверн' in content or 'account' in content

    def test_2_3_wrong_password(self, client, user_common):
        """2.3: Неверный пароль → ошибка"""
        response = client.post(reverse('account_login'), {
            'login': 'test_common', 'password': 'WrongPass123'
        })
        assert response.status_code == 200
        content = response.content.decode().lower()
        assert 'incorrect' in content or 'неверн' in content or 'account' in content

    def test_2_4_successful_login(self, client, user_common):
        """2.4: Успешный вход → редирект на /news/"""
        response = client.post(reverse('account_login'), {
            'login': 'test_common', 'password': 'TestPass123'
        })
        assert response.status_code == 302
        assert '/news/' in response.url or response.url == '/'


@pytest.mark.django_db
class TestLogout:
    """Тесты выхода"""

    def test_3_1_logout(self, client, user_common):
        """3.1: Выход → редирект"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('account_logout'))
        assert response.status_code == 302

    def test_3_2_access_after_logout(self, client, user_common):
        """3.2: Доступ после выхода → редирект на login"""
        client.login(username='test_common', password='TestPass123')
        client.post(reverse('account_logout'))
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url