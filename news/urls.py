# news/urls.py
from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # =============================================================================
    # СПИСОК И ПОИСК
    # =============================================================================
    path('', views.PostList.as_view(), name='post_list'),
    path('search/', views.PostSearch.as_view(), name='search'),

    # =============================================================================
    # ДЕТАЛЬНЫЙ ПРОСМОТР
    # =============================================================================
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),

    # =============================================================================
    # СОЗДАНИЕ (разделено по типу поста)
    # =============================================================================
    path('news/create/', views.PostCreate.as_view(), name='news_create'),
    path('article/create/', views.PostCreate.as_view(), name='article_create'),

    # =============================================================================
    # РЕДАКТИРОВАНИЕ (разделено по типу поста)
    # =============================================================================
    path('news/<int:pk>/edit/', views.PostUpdate.as_view(), name='news_edit'),
    path('article/<int:pk>/edit/', views.PostUpdate.as_view(), name='article_edit'),

    # =============================================================================
    # УДАЛЕНИЕ — ⚠️ ВРЕМЕННЫЕ ЗАГЛУШКИ
    # =============================================================================
    path('news/<int:pk>/delete/', views.PostDetail.as_view(), name='news_delete'),  # ⚠️ ЗАГЛУШКА
    path('article/<int:pk>/delete/', views.PostDetail.as_view(), name='article_delete'),  # ⚠️ ЗАГЛУШКА

    # =============================================================================
    # ПОДПИСКИ НА КАТЕГОРИИ
    # =============================================================================
    path('subscribe/<int:category_pk>/', views.SubscribeToggleView.as_view(), name='subscribe'),
    path('subscriptions/', views.SubscriptionsListView.as_view(), name='subscriptions'),

    # =============================================================================
    # КОММЕНТАРИИ
    # =============================================================================
    path('post/<int:pk>/', views.post_detail, name='post_with_comments'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:pk>/dislike/', views.dislike_comment, name='dislike_comment'),
]