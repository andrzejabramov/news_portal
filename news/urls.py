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
    # УДАЛЕНИЕ — ⚠️ ВРЕМЕННЫЕ ЗАГЛУШКИ (TODO: реализовать PostDelete)
    # =============================================================================
    # TODO(#DELETE-001): Добавить класс PostDelete в news/views.py
    # TODO(#DELETE-001): Заменить PostDetail.as_view() на PostDelete.as_view() ниже
    # Файлы для правки: news/views.py, news/urls.py
    # Приоритет: после завершения модуля email-уведомлений
    # Шаблоны: templates/post_delete.html (уже готов)

    path('news/<int:pk>/delete/', views.PostDetail.as_view(), name='news_delete'),  # ⚠️ ЗАГЛУШКА
    path('article/<int:pk>/delete/', views.PostDetail.as_view(), name='article_delete'),  # ⚠️ ЗАГЛУШКА
]