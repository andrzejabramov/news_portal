# tests/test_permissions.py
import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from news.models import Post, Author


@pytest.mark.django_db
class TestGroupPermissions:
    """Тесты групп и прав доступа (Раздел 4)"""

    def test_4_1_new_user_in_common(self, client):
        """4.1: Новый пользователь автоматически в группе 'common'"""
        client.post(reverse('account_signup'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        })
        user = User.objects.get(username='newuser')
        assert user.groups.filter(name='common').exists(), "Новый пользователь должен быть в группе 'common'"

    def test_4_2_common_cannot_create_news(self, client, user_common):
        """4.2: Группа common → создание новости (403)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 403, "Группа common не должна иметь доступ к созданию новостей"

    def test_4_3_common_cannot_edit(self, client, user_common, sample_post):
        """4.3: Группа common → редактирование (403)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_edit', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 403, "Группа common не должна иметь доступ к редактированию"

    def test_4_4_common_cannot_delete(self, client, user_common, sample_post):
        """4.4: Группа common → удаление (403 или 404)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_delete', kwargs={'pk': sample_post.pk}))
        # PostDelete использует get_queryset, который фильтрует по автору
        # Поэтому чужой пост не найдётся → 404
        assert response.status_code in [403, 404], "Группа common не должна иметь доступ к удалению"

    def test_4_6_author_can_create(self, client, user_author):
        """4.6: Группа authors → создание (доступ есть)"""
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 200, "Группа authors должна иметь доступ к созданию новостей"

    def test_4_7_author_can_edit_own(self, client, user_author, sample_post):
        """4.7: Группа authors → редактирование своего (доступ есть)"""
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_edit', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 200, "Автор должен иметь доступ к редактированию своего поста"

    def test_4_8_author_cannot_edit_others(self, client, user_author, user_common):
        """4.8: Группа authors → редактирование чужого (404, т.к. пост не в queryset)"""
        # Создаём пост от имени другого пользователя
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile,
            title='Чужой пост',
            text='Текст',
            type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_edit', kwargs={'pk': other_post.pk}))
        # 404 — пост не найден в queryset (фильтр по автору)
        # 403 — если бы была только PermissionRequiredMixin
        assert response.status_code in [403, 404], "Нельзя редактировать чужие посты"

    def test_4_9_author_can_delete_own(self, client, user_author, sample_post):
        """4.9: Группа authors → удаление своего (доступ есть)"""
        client.login(username='test_author', password='TestPass123')
        response = client.get(reverse('news:news_delete', kwargs={'pk': sample_post.pk}))
        assert response.status_code == 200, "Автор должен иметь доступ к удалению своего поста"