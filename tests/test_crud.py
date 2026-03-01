# tests/test_crud.py
import pytest
from django.urls import reverse
from news.models import Post, Author, Category


@pytest.mark.django_db
class TestPostCreate:
    """Тесты создания постов"""

    def test_6_1_create_news_sets_type_news(self, client, user_author, sample_category):
        """6.1: Создание новости → type=NEWS"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_create'), {
            'title': 'Тестовая новость', 'text': 'Текст новости',
            'categories': [sample_category.pk]
        })
        if response.status_code == 200 and response.context and 'form' in response.context:
            print(f"❌ Ошибки формы: {response.context['form'].errors}")
        assert response.status_code == 302
        post = Post.objects.get(title='Тестовая новость')
        assert post.type == Post.NEWS

    def test_6_2_create_article_sets_type_article(self, client, user_author, sample_category):
        """6.2: Создание статьи → type=ARTICLE"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:article_create'), {
            'title': 'Тестовая статья', 'text': 'Текст статьи',
            'categories': [sample_category.pk]
        })
        if response.status_code == 200 and response.context and 'form' in response.context:
            print(f"❌ Ошибки формы: {response.context['form'].errors}")
        assert response.status_code == 302
        post = Post.objects.get(title='Тестовая статья')
        assert post.type == Post.ARTICLE

    def test_6_3_author_set_from_request_user(self, client, user_author, sample_category):
        """6.3: Автор устанавливается из request.user.author"""
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_create'), {
            'title': 'Пост с автором', 'text': 'Текст',
            'categories': [sample_category.pk]
        })
        if response.status_code == 200 and response.context and 'form' in response.context:
            print(f"❌ Ошибки формы: {response.context['form'].errors}")
        assert response.status_code == 302
        post = Post.objects.get(title='Пост с автором')
        assert post.author.user == user_author

    def test_6_4_create_without_permission(self, client, user_common):
        """6.4: Без права add_post → 403"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:news_create'))
        assert response.status_code == 403


@pytest.mark.django_db
class TestPostUpdate:
    """Тесты редактирования постов"""

    def test_6_5_update_own_post(self, client, user_author, sample_post, sample_category):
        """6.5: Редактирование своего поста → успех"""
        client.login(username='test_author', password='TestPass123')
        sample_post.categories.add(sample_category)
        response = client.post(reverse('news:news_edit', kwargs={'pk': sample_post.pk}), {
            'title': 'Обновлённый заголовок', 'text': 'Обновлённый текст',
            'categories': [sample_category.pk]
        })
        if response.status_code == 200 and response.context and 'form' in response.context:
            print(f"❌ Ошибки формы: {response.context['form'].errors}")
        assert response.status_code == 302
        sample_post.refresh_from_db()
        assert sample_post.title == 'Обновлённый заголовок'

    def test_6_6_update_others_post(self, client, user_author, user_common):
        """6.6: Редактирование чужого поста → 403 с сообщением"""
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile, title='Чужой пост', text='Текст', type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_edit', kwargs={'pk': other_post.pk}), {
            'title': 'Попытка взлома', 'text': 'Текст', 'categories': []
        })
        # Теперь ожидаем 403, а не 404!
        assert response.status_code == 403
        content = response.content.decode()
        assert 'отсутствуют права' in content or 'permissions' in content.lower()


@pytest.mark.django_db
class TestPostDelete:
    """Тесты удаления постов"""

    def test_6_7_delete_own_post(self, client, user_author, sample_post):
        """6.7: Удаление своего поста → успех"""
        client.login(username='test_author', password='TestPass123')
        post_pk = sample_post.pk
        response = client.post(reverse('news:news_delete', kwargs={'pk': post_pk}))
        assert response.status_code == 302
        assert not Post.objects.filter(pk=post_pk).exists()

    def test_6_8_delete_others_post(self, client, user_author, user_common):
        """6.8: Удаление чужого поста → 403 с сообщением"""
        author_profile, _ = Author.objects.get_or_create(user=user_common)
        other_post = Post.objects.create(
            author=author_profile, title='Чужой пост', text='Текст', type=Post.NEWS
        )
        client.login(username='test_author', password='TestPass123')
        response = client.post(reverse('news:news_delete', kwargs={'pk': other_post.pk}))
        # Теперь ожидаем 403, а не 404!
        assert response.status_code == 403
        content = response.content.decode()
        assert 'отсутствуют права' in content or 'permissions' in content.lower()
        # Пост НЕ удалён
        assert Post.objects.filter(pk=other_post.pk).exists()