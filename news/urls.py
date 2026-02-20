# news/urls.py
from django.urls import path
from .views import (
    PostList,
    PostDetail,
    PostSearch,
    PostCreate,
    PostUpdate,
    PostDelete,
)

app_name = "news"

urlpatterns = [
    path("", PostList.as_view(), name="post_list"),
    path("<int:pk>/", PostDetail.as_view(), name="post_detail"),
    path("search/", PostSearch.as_view(), name="search"),

    # Создание
    path('news/create/', PostCreate.as_view(), name='news_create'),
    path('articles/create/', PostCreate.as_view(), name='article_create'),

    # Редактирование
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_edit'),
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='article_edit'),

    # Удаление
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
]
