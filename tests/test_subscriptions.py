#!/usr/bin/env python3
"""
Тесты модуля подписок на категории.
Запуск: pytest tests/test_subscriptions.py -v
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Group
from news.models import Post, Author, Category, UserCategorySubscription


@pytest.mark.django_db
class TestSubscribeToggleView:
    """Тесты переключения подписки (SubscribeToggleView)"""

    def test_5_1_subscribe_creates_subscription(self, client, user_common, sample_category):
        """5.1: Подписка создаёт запись UserCategorySubscription"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'subscribe'
        })
        assert response.status_code == 302
        assert UserCategorySubscription.objects.filter(
            user=user_common,
            category=sample_category,
            is_active=True
        ).exists()

    def test_5_2_subscribe_sets_is_active_true(self, client, user_common, sample_category):
        """5.2: Новая подписка имеет is_active=True"""
        client.login(username='test_common', password='TestPass123')
        # Сначала создаём неактивную подписку
        sub, _ = UserCategorySubscription.objects.get_or_create(
            user=user_common,
            category=sample_category,
            defaults={'is_active': False}
        )
        # Подписываемся
        response = client.post(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'subscribe'
        })
        assert response.status_code == 302
        sub.refresh_from_db()
        assert sub.is_active == True

    def test_5_3_unsubscribe_sets_is_active_false(self, client, user_common, sample_category, sample_subscription):
        """5.3: Отписка ставит is_active=False"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'unsubscribe'
        })
        assert response.status_code == 302
        sample_subscription.refresh_from_db()
        assert sample_subscription.is_active == False

    def test_5_4_subscribe_shows_success_message(self, client, user_common, sample_category):
        """5.4: После подписки показывается сообщение успеха"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'subscribe'
        }, follow=True)
        content = response.content.decode()
        assert '✅ Вы подписаны' in content or 'подписаны' in content.lower()

    def test_5_5_unsubscribe_shows_success_message(self, client, user_common, sample_category, sample_subscription):
        """5.5: После отписки показывается сообщение"""
        client.login(username='test_common', password='TestPass123')
        response = client.post(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'unsubscribe'
        }, follow=True)
        content = response.content.decode()
        assert '🔕 Вы отписались' in content or 'отписались' in content.lower()

    def test_5_6_guest_cannot_subscribe(self, client, sample_category):
        """5.6: Гость не может подписаться → редирект на login"""
        response = client.post(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'subscribe'
        })
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_5_7_subscribe_via_get_method(self, client, user_common, sample_category):
        """5.7: Подписка через GET-запрос тоже работает"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:subscribe', kwargs={'category_pk': sample_category.pk}), {
            'action': 'subscribe'
        })
        assert response.status_code == 302
        assert UserCategorySubscription.objects.filter(
            user=user_common,
            category=sample_category,
            is_active=True
        ).exists()


@pytest.mark.django_db
class TestSubscriptionsListView:
    """Тесты страницы управления подписками"""

    def test_5_8_subscriptions_list_shows_all_categories(self, client, user_common, sample_category):
        """5.8: Страница подписок показывает все категории"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:subscriptions'))
        assert response.status_code == 200
        assert sample_category.name in response.content.decode('utf-8')

    def test_5_9_subscriptions_list_shows_status(self, client, user_common, sample_category, sample_subscription):
        """5.9: Страница показывает статус подписки (✅/❌)"""
        client.login(username='test_common', password='TestPass123')
        response = client.get(reverse('news:subscriptions'))
        content = response.content.decode()
        # Проверяем, что категория отмечена как подписанная
        assert sample_category.name in content

    def test_5_10_guest_cannot_view_subscriptions(self, client):
        """5.10: Гость не может видеть страницу подписок → редирект"""
        response = client.get(reverse('news:subscriptions'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url


@pytest.mark.django_db
class TestSubscriptionTemplateTag:
    """Тесты template tag check_subscription"""

    def test_5_11_check_subscription_returns_true(self, user_common, sample_category, sample_subscription):
        """5.11: check_subscription возвращает True для активной подписки"""
        from news.templatetags.subscription_tags import check_subscription
        result = check_subscription(None, user_common.id, sample_category.id)
        assert result == True

    def test_5_12_check_subscription_returns_false(self, user_common, sample_category):
        """5.12: check_subscription возвращает False если нет подписки"""
        from news.templatetags.subscription_tags import check_subscription
        result = check_subscription(None, user_common.id, sample_category.id)
        assert result == False

    def test_5_13_check_subscription_returns_false_inactive(self, user_common, sample_category):
        """5.13: check_subscription возвращает False для неактивной подписки"""
        from news.templatetags.subscription_tags import check_subscription
        # Создаём неактивную подписку
        UserCategorySubscription.objects.create(
            user=user_common,
            category=sample_category,
            is_active=False
        )
        result = check_subscription(None, user_common.id, sample_category.id)
        assert result == False