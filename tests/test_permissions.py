# tests/test_permissions.py
import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from news.models import Post, Author


@pytest.mark.django_db
class TestGroupPermissions:
    """Тесты групп и прав доступа"""

    def test_4_1_new_user_in_common(self, client):
        """4.1: Новый пользователь автоматически в группе 'common'"""
        client.post(reverse('account_signup'), {
            'username': 'newuser', 'email': 'newuser@test.com',
            'password1': 'TestPass123', 'password2': 'TestPass123'
        })
        user = User.objects.get(username='newuser')
        assert user.groups.filter(name='common').exists()

    def test_4_2_common_cannot_create_news(self, client, user_common):
        """4.2: Группа common → создание новости (403)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 403

    def test_4_3_common_cannot_edit(self, client, user_common, sample_post):
        """4.3: Группа common → редактирование (403)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_edit', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 403

    def test_4_4_common_cannot_delete(self, client, user_common, sample_post):
        """4.4: Группа common → удаление (403)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_delete', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 403

    def test_4_6_author_can_create(self, client, user_author):
        """4.6: Группа authors → создание (доступ есть)"""
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 200

    def test_4_7_author_can_edit_own(self, client, user_author, sample_post):
        """4.7: Группа authors → редактирование своего (доступ есть)"""
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_edit', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 200

    def test_4_8_author_cannot_edit_others(self, client, user_author, user_common):
        """4.8: Редактирование чужого поста → 403 с человеко-читаемым сообщением"""
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile, title='Чужой пост', text='Текст', type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_edit', kwargs={'pk': other_post.pk}))
        # Теперь ожидаем 403 с понятным сообщением (не 404!)
        assert response.status_code == 403
        content = response.content.decode()
        assert 'отсутствуют права' in content or 'permissions' in content.lower()

    def test_4_9_author_can_delete_own(self, client, user_author, sample_post):
        """4.9: Удаление своего поста (доступ есть)"""
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_delete', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 200

    def test_4_10_author_cannot_delete_others(self, client, user_author, user_common):
        """4.10: Удаление чужого поста → 403 с сообщением"""
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile, title='Чужой пост', text='Текст', type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_delete', kwargs={'pk': other_post.pk}))
        assert response.status_code == 403
        content = response.content.decode()
        assert 'отсутствуют права' in content or 'permissions' in content.lower()