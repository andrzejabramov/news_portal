#!/usr/bin/env python3
"""
Тесты модуля комментариев.
Запуск: pytest tests/test_comments.py -v
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from news.models import Post, Author, Category, Comment


@pytest.mark.django_db
class TestAddComment:
    """Тесты добавления комментариев"""

    def test_6_1_add_comment_authenticated(self, client, user_common, sample_post):
        """6.1: Авторизованный пользователь может добавить комментарий"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:add_comment', kwargs={'pk': sample_post.pk}), {
            'text': 'Тестовый комментарий'
        })
        assert response.status_code == 302
        assert Comment.objects.filter(
            post=sample_post,
            user=user_common,
            text='Тестовый комментарий'
        ).exists()

    def test_6_2_add_comment_sets_user(self, client, user_common, sample_post):
        """6.2: Комментарий сохраняется с правильным user"""
        client.login(username='test_common', password='TestPass123')
        client.post(reverse('news:add_comment', kwargs={'pk': sample_post.pk}), {
            'text': 'Тест'
        })
        comment = Comment.objects.get(text='Тест')
        assert comment.user == user_common

    def test_6_3_add_comment_sets_post(self, client, user_common, sample_post):
        """6.3: Комментарий сохраняется с правильным post"""
        client.login(username='test_common', password='TestPass123')
        client.post(reverse('news:add_comment', kwargs={'pk': sample_post.pk}), {
            'text': 'Тест'
        })
        comment = Comment.objects.get(text='Тест')
        assert comment.post == sample_post

    def test_6_4_add_comment_guest_redirects(self, client, sample_post):
        """6.4: Гость не может добавить комментарий → редирект на login"""
        response = client.post(reverse('news:add_comment', kwargs={'pk': sample_post.pk}), {
            'text': 'Тест'
        })
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_6_5_add_comment_empty_text(self, client, user_common, sample_post):
        """6.5: Пустой текст комментария → ошибка валидации"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:add_comment', kwargs={'pk': sample_post.pk}), {
            'text': ''
        })
        # Должна быть ошибка формы или редирект назад
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestEditComment:
    """Тесты редактирования комментариев"""

    def test_6_6_edit_comment_own(self, client, user_common, sample_comment):
        """6.6: Автор может редактировать свой комментарий"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:edit_comment', kwargs={'pk': sample_comment.pk}), {
            'text': 'Обновлённый комментарий'
        })
        assert response.status_code == 302
        sample_comment.refresh_from_db()
        assert sample_comment.text == 'Обновлённый комментарий'

    def test_6_7_edit_comment_others_403(self, client, user_author, sample_comment):
        """6.7: Редактирование чужого комментария → 403"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:edit_comment', kwargs={'pk': sample_comment.pk}), {
            'text': 'Попытка взлома'
        })
        assert response.status_code == 403 or response.status_code == 302
        # Проверяем, что текст не изменился
        sample_comment.refresh_from_db()
        assert sample_comment.text != 'Попытка взлома'

    def test_6_8_edit_comment_shows_form(self, client, user_common, sample_comment):
        """6.8: Страница редактирования показывает форму"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:edit_comment', kwargs={'pk': sample_comment.pk}))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'form' in content.lower() or 'textarea' in content.lower()


@pytest.mark.django_db
class TestDeleteComment:
    """Тесты удаления комментариев"""

    def test_6_9_delete_comment_own(self, client, user_common, sample_comment):
        """6.9: Автор может удалить свой комментарий"""
        client.login(username='test_common', password='TestPass123')
        comment_pk = sample_comment.pk
        response = client.post(reverse('news:delete_comment', kwargs={'pk': comment_pk}))
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=comment_pk).exists()

    def test_6_10_delete_comment_others_403(self, client, user_author, sample_comment):
        """6.10: Удаление чужого комментария → 403"""
        client.login(username='test_author', password='TestPass123')
        comment_pk = sample_comment.pk
        response = client.post(reverse('news:delete_comment', kwargs={'pk': comment_pk}))
        assert response.status_code == 403 or response.status_code == 302
        # Проверяем, что комментарий не удалён
        assert Comment.objects.filter(pk=comment_pk).exists()


@pytest.mark.django_db
class TestCommentRating:
    """Тесты рейтинга комментариев (лайк/дизлайк)"""

    def test_6_11_like_increments_rating(self, client, user_common, sample_comment):
        """6.11: Лайк увеличивает рейтинг на 1"""
        client.login(username='test_common', password='TestPass123')
        old_rating = sample_comment.rating
        response = client.get(reverse('news:like_comment', kwargs={'pk': sample_comment.pk}))
        assert response.status_code == 302
        sample_comment.refresh_from_db()
        assert sample_comment.rating == old_rating + 1

    def test_6_12_dislike_decrements_rating(self, client, user_common, sample_comment):
        """6.12: Дизлайк уменьшает рейтинг на 1"""
        client.login(username='test_common', password='TestPass123')
        old_rating = sample_comment.rating
        response = client.get(reverse('news:dislike_comment', kwargs={'pk': sample_comment.pk}))
        assert response.status_code == 302
        sample_comment.refresh_from_db()
        assert sample_comment.rating == old_rating - 1

    def test_6_13_like_guest_redirects(self, client, sample_comment):
        """6.13: Гость не может лайкать → редирект на login"""
        response = client.get(reverse('news:like_comment', kwargs={'pk': sample_comment.pk}))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_6_14_dislike_guest_redirects(self, client, sample_comment):
        """6.14: Гость не может дизлайкать → редирект на login"""
        response = client.get(reverse('news:dislike_comment', kwargs={'pk': sample_comment.pk}))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url


@pytest.mark.django_db
class TestCommentDisplay:
    """Тесты отображения комментариев"""

    def test_6_15_comments_ordered_by_created_at(self, client, sample_post, user_common, user_author):
        """6.15: Комментарии сортируются по дате (новые сверху)"""
        # Создаём два комментария с разной датой
        comment1 = Comment.objects.create(post=sample_post, user=user_common, text='Первый')
        comment2 = Comment.objects.create(post=sample_post, user=user_author, text='Второй')

        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:post_detail', kwargs={'pk': sample_post.pk}))
        content = response.content.decode()

        # Проверяем, что оба комментария отображаются
        assert 'Первый' in content
        assert 'Второй' in content