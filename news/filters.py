# news/filters.py
import django_filters
from django import forms
from datetime import datetime
from .models import Post


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по заголовку'
        })
    )
    author = django_filters.CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Автор',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя автора'
        })
    )
    # ← Возвращаем фильтр даты
    created_after = django_filters.CharFilter(
        field_name='created_at',
        label='Дата от',
        method='filter_by_date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'author', 'created_after']

    # ← Фильтр: новости ПОЗЖЕ указанной даты (≥)
    def filter_by_date(self, queryset, name, value):
        if not value:
            return queryset
        try:
            date_obj = datetime.strptime(value, '%Y-%m-%d').date()
            return queryset.filter(created_at__date__gte=date_obj)
        except (ValueError, TypeError):
            return queryset

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ← Фильтруем только новости
        self.queryset = self.queryset.filter(type=Post.NEWS)