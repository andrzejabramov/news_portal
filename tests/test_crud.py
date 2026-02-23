# tests/test_crud.py
import pytest
from django.urls import reverse
from news.models import Post, Author, Category


@pytest.mark.django_db
class TestPostCreate:
    """Тесты создания постов (Раздел 6)"""

    def test_6_1_create_news_sets_type_news(self, client, user_author, sample_category):
        """6.1: Создание новости → type=NEWS из URL"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_create'), {
            'title': 'Тестовая новость',
            'text': 'Текст новости',
            'categories': [sample_category.pk]  # ← Передаём ID категории!
        })
        # Для отладки: если статус 200, выводим ошибки формы
        if response.status_code == 200:
            print(f"❌ Ошибки формы: {response.context['form'].errors if response.context else 'No context'}")
        assert response.status_code == 302, f"Ожидался редирект, получен статус {response.status_code}"

        post = Post.objects.get(title='Тестовая новость')
        assert post.type == Post.NEWS, f"Ожидался тип NEWS, получен {post.type}"

    def test_6_2_create_article_sets_type_article(self, client, user_author, sample_category):
        """6.2: Создание статьи → type=ARTICLE из URL"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:article_create'), {
            'title': 'Тестовая статья',
            'text': 'Текст статьи',
            'categories': [sample_category.pk]  # ← Передаём ID категории!
        })
        if response.status_code == 200:
            print(f"❌ Ошибки формы: {response.context['form'].errors if response.context else 'No context'}")
        assert response.status_code == 302

        post = Post.objects.get(title='Тестовая статья')
        assert post.type == Post.ARTICLE, f"Ожидался тип ARTICLE, получен {post.type}"

    def test_6_3_author_set_from_request_user(self, client, user_author, sample_category):
        """6.3: Автор устанавливается из request.user.author"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_create'), {
            'title': 'Пост с автором',
            'text': 'Текст',
            'categories': [sample_category.pk]  # ← Передаём ID категории!
        })
        if response.status_code == 200:
            print(f"❌ Ошибки формы: {response.context['form'].errors if response.context else 'No context'}")
        assert response.status_code == 302

        post = Post.objects.get(title='Пост с автором')
        assert post.author.user == user_author, "Автор поста должен совпадать с текущим пользователем"

    def test_6_4_create_without_permission(self, client, user_common):
        """6.4: Без права add_post → 403"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 403, "Группа common не должна иметь право создания постов"


@pytest.mark.django_db
class TestPostUpdate:
    """Тесты редактирования постов"""

    def test_6_5_update_own_post(self, client, user_author, sample_post, sample_category):
        """6.5: Редактирование своего поста → успех"""
        client.login(username='test_author', password='TestPass123')
        # Добавляем категорию к существующему посту (если нет)
        sample_post.categories.add(sample_category)

        response = client.post(reverse('news:news_edit', kwargs={'pk': sample_post.pk}), {
            'title': 'Обновлённый заголовок',
            'text': 'Обновлённый текст',
            'categories': [sample_category.pk]  # ← Передаём ID категории!
        })
        if response.status_code == 200:
            print(f"❌ Ошибки формы: {response.context['form'].errors if response.context else 'No context'}")
        assert response.status_code == 302

        sample_post.refresh_from_db()
        assert sample_post.title == 'Обновлённый заголовок'

    def test_6_6_update_others_post(self, client, user_author, user_common):
        """6.6: Редактирование чужого поста → 404"""
        # Создаём чужой пост
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile,
            title='Чужой пост',
            text='Текст',
            type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_edit', kwargs={'pk': other_post.pk}), {
            'title': 'Попытка взлома',
            'text': 'Текст',
            'categories': []
        })
        # 404 — пост не найден в queryset (фильтр по автору)
        assert response.status_code == 404


@pytest.mark.django_db
class TestPostDelete:
    """Тесты удаления постов"""

    def test_6_7_delete_own_post(self, client, user_author, sample_post):
        """6.7: Удаление своего поста → успех"""
        client.login(username='test_author', password='TestPass123')
        post_pk = sample_post.pk
        response = client.post(reverse('news:news_delete', kwargs={'pk': post_pk}))
        assert response.status_code == 302

        # Пост удалён
        assert not Post.objects.filter(pk=post_pk).exists()

    def test_6_8_delete_others_post(self, client, user_author, user_common):
        """6.8: Удаление чужого поста → 404"""
        # Создаём чужой пост
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile,
            title='Чужой пост для удаления',
            text='Текст',
            type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_delete', kwargs={'pk': other_post.pk}))
        # 404 — пост не найден в queryset
        assert response.status_code == 404

        # Пост НЕ удалён
        assert Post.objects.filter(pk=other_post.pk).exists()