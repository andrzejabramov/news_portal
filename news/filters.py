# news/filters.py
import django_filters
from django import forms
from datetime import datetime, time
from .models import Post


class PostFilter(django_filters.FilterSet):
    """Фильтр для поиска постов (регистронезависимый + trim + фикс дат)"""

    title = django_filters.CharFilter(
        label='Название содержит',
        method='filter_title'
    )

    def filter_title(self, queryset, name, value):
        """Python-фильтрация для SQLite + кириллица"""
        if value and value.strip():
            search_term = value.strip().lower()
            return queryset.filter(
                id__in=[
                    post.id for post in queryset
                    if search_term in post.title.lower()
                ]
            )
        return queryset

    author = django_filters.CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Автор',
        method='filter_author'
    )

    def filter_author(self, queryset, name, value):
        """Trim + поиск по автору"""
        if value and value.strip():
            return queryset.filter(author__user__username__icontains=value.strip())
        return queryset

    created_at_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Дата с',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'style': 'width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px;'
        })
    )

    created_at_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Дата по',
        method='filter_date_before'  # ← ← ← Кастомный метод!
    )

    def filter_date_before(self, queryset, name, value):
        """
        Добавляем 23:59:59 к конечной дате, чтобы включить весь день.
        Пример: 12.07.2025 → 2025-07-12 23:59:59
        """
        if value:
            # Преобразуем дату в datetime с концом дня
            end_of_day = datetime.combine(value, time(23, 59, 59))
            return queryset.filter(created_at__lte=end_of_day)
        return queryset

    class Meta:
        model = Post
        fields = []