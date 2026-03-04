# tests/conftest.py
import pytest
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from news.models import Author, Post, Category


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Разрешаем доступ к БД для всех тестов"""
    pass


@pytest.fixture(autouse=True)
def setup_site_and_socialapp(db):
    """Настраиваем Site и SocialApp для Yandex (автоматически для всех тестов)"""
    # Настраиваем текущий сайт
    site = Site.objects.get_current()
    site.domain = 'testserver'
    site.name = 'Test Site'
    site.save()

    # Создаём SocialApp для Yandex
    socialapp, _ = SocialApp.objects.get_or_create(
        provider='yandex',
        defaults={
            'name': 'Yandex',
            'client_id': 'test_client_id',
            'secret': 'test_secret',
        }
    )
    socialapp.sites.add(site)
    return socialapp


@pytest.fixture
def common_group():
    """Группа 'common' — базовые права"""
    group, _ = Group.objects.get_or_create(name='common')
    return group


@pytest.fixture
def authors_group():
    """Группа 'authors' — с правами add_post и change_post"""
    group, _ = Group.objects.get_or_create(name='authors')

    content_type = ContentType.objects.get_for_model(Post)

    add_perm, _ = Permission.objects.get_or_create(
        codename='add_post',
        content_type=content_type,
        defaults={'name': 'Can add post'}
    )
    change_perm, _ = Permission.objects.get_or_create(
        codename='change_post',
        content_type=content_type,
        defaults={'name': 'Can change post'}
    )
    group.permissions.set([add_perm, change_perm])
    return group


@pytest.fixture
def user_common(db, common_group):
    """Пользователь в группе 'common' (без прав на CRUD)"""
    user = User.objects.create_user(
        username='test_common',
        email='common@test.com',
        password='TestPass123'
    )
    user.groups.add(common_group)
    return user


@pytest.fixture
def user_author(db, authors_group):
    """Пользователь в группе 'authors' (с правами на CRUD)"""
    user = User.objects.create_user(
        username='test_author',
        email='author@test.com',
        password='TestPass123'
    )
    user.groups.add(authors_group)
    # Создаём профиль Author, т.к. views ожидают user.author
    Author.objects.get_or_create(user=user)
    return user


@pytest.fixture
def sample_post(db, user_author):
    """Тестовая новость от автора"""
    return Post.objects.create(
        author=user_author.author,  # ← важно: через профиль Author!
        title='Тестовая новость',
        text='Текст тестовой новости',
        type=Post.NEWS
    )


# @pytest.fixture
# def sample_category(db):
#     """Тестовая категория"""
#     from news.models import Category
#     category, _ = Category.objects.get_or_create(name='Тестовая категория')
#     return category


@pytest.fixture
def sample_category(db):
    """Фикстура для тестовой категории"""
    return Category.objects.create(name='Тестовая категория')


# =============================================================================
# ФИКСТУРЫ ДЛЯ КОММЕНТАРИЕВ И ПОДПИСОК
# =============================================================================

@pytest.fixture
def sample_comment(db, sample_post, user_common):
    """Тестовый комментарий к посту"""
    from news.models import Comment
    return Comment.objects.create(
        post=sample_post,
        user=user_common,
        text='Тестовый комментарий'
    )


@pytest.fixture
def sample_subscription(db, user_common, sample_category):
    """Активная подписка пользователя на категорию"""
    from news.models import UserCategorySubscription
    sub, _ = UserCategorySubscription.objects.get_or_create(
        user=user_common,
        category=sample_category,
        defaults={'is_active': True}
    )
    return sub


@pytest.fixture(autouse=True)
def use_console_email_backend_for_tests(settings):
    """Все тесты email используют console backend"""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'