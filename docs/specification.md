# 📚 News Portal — Документация проекта

**Django Web Application**  
**Версия:** 1.0  
**Дата:** Февраль 2026

---

## 📋 Содержание

1. [Обзор проекта](#1-обзор-проекта)
2. [Архитектура MTV](#2-архитектура-mtv)
3. [Реализованный функционал](#3-реализованный-функционал)
4. [Структура проекта](#4-структура-проекта)
5. [Тестирование и проверка](#5-тестирование-и-проверка)
6. [Зависимости](#6-зависимости)
7. [Развёртывание](#7-развёртывание)

---

## 1. Обзор проекта

**News Portal** — это веб-приложение для публикации новостей и статей с системой аутентификации, авторизации и разграничения прав доступа.

### 🎯 Основные возможности

| Функция | Описание |
|---------|----------|
| 📰 **Публикации** | Создание новостей и статей с категориями |
| 🔍 **Поиск** | Фильтрация по названию, автору, дате |
| 📄 **Пагинация** | Постраничный вывод (10 записей на странице) |
| 👤 **Авторизация** | Вход через форму и Yandex OAuth |
| 🔐 **Права доступа** | Группы `common` и `authors` с разными правами |
| ✏️ **CRUD** | Создание, редактирование, удаление публикаций |
| ⭐ **Рейтинг** | Автоматический расчёт рейтинга публикаций |
| 🛡️ **Цензура** | Фильтр запрещённых слов в шаблонах |

---

## 2. Архитектура MTV

### 🏗️ Почему выбран Django (MTV)?

| Критерий | Обоснование |
|----------|-------------|
| **Быстрая разработка** | Встроенная админ-панель, ORM, аутентификация |
| **Безопасность** | CSRF, XSS, SQL Injection защита из коробки |
| **Масштабируемость** | Чёткое разделение слоёв, легко поддерживать |
| **Сообщество** | Огромное количество пакетов и документации |

### 📐 Схема взаимодействия слоёв

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                        │
│                      HTTP Request / Response                    │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                          URLs (urls.py)                         │
│                    Маршрутизация запросов                       │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                      VIEWS (views.py)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   ListView      │  │   DetailView    │  │   CreateView    │  │
│  │   (список)      │  │   (детали)      │  │   (создание)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   UpdateView    │  │   DeleteView    │  │   FilterView    │  │
│  │   (ред.)        │  │   (удаление)    │  │   (поиск)       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                      MODELS (models.py)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐  │
│  │    Post     │  │   Author    │  │  Category   │  │ Comment│  │
│  │ (публикации)│  │  (авторы)   │  │ (категории) │  │(коммен)│  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘  │
│                      Django ORM (SQLite)                        │
└─────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                    TEMPLATES (.html files)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌────────-─────┐  ┌────────┐ │
│  │  news.html  │  │   new.html  │  │post_edit.html│  │login   │ │
│  │  (список)   │  │  (детали)   │  │ (форма)      │  │.html   │ │
│  └─────────────┘  └─────────────┘  └───────────-──┘  └────────┘ │
│                 Django Template Language (DTL)                  │
└─────────────────────────────────────────────────────────────────┘
```

### 🔄 Поток данных (Request → Response)

```
1. Пользователь → GET /news/
2. URL Router → news.urls → PostList.as_view()
3. View → Post.objects.filter(type=NEWS).order_by('-created_at')
4. View → paginate_by=10 → Page 1 of 2
5. View → render('news.html', {'news': page_obj})
6. Template → {{ news.title }}, {% for item in news %}
7. Response → HTML → Browser
```

---

## 3. Реализованный функционал

### 3.1 Пагинация

**Файл:** `news/views.py`

```python
class PostList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10  # ← 10 новостей на странице
```

**Почему именно так:**
- ✅ `paginate_by` — встроенная пагинация Django, не нужно писать вручную
- ✅ `ordering = '-created_at'` — свежие новости сверху
- ✅ `context_object_name = 'news'` — понятное имя переменной в шаблоне

**Шаблон пагинации:** `templates/news.html`

```html
{% if is_paginated %}
<div class="pagination">
    <span>Страница {{ page_obj.number }} из {{ page_obj.paginator.num_pages }}</span>
    
    {% if page_obj.has_previous %}
        <a href="?page=1">« Первая</a>
        <a href="?page={{ page_obj.previous_page_number }}">‹ Назад</a>
    {% endif %}
    
    {% for num in page_obj.paginator.page_range %}
        {% if page_obj.number == num %}
            <span class="current">{{ num }}</span>
        {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
            <a href="?page={{ num }}">{{ num }}</a>
        {% endif %}
    {% endfor %}
    
    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">Вперед ›</a>
        <a href="?page={{ page_obj.paginator.num_pages }}">Последняя »</a>
    {% endif %}
</div>
{% endif %}
```

---

### 3.2 Поиск и фильтрация

**Файл:** `news/filters.py`

```python
import django_filters
from django import forms
from datetime import datetime
from .models import Post

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    author = django_filters.CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Автор',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    created_after = django_filters.CharFilter(
        field_name='created_at',
        label='Дата от',
        method='filter_by_date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def filter_by_date(self, queryset, name, value):
        if not value:
            return queryset
        try:
            date_obj = datetime.strptime(value, '%Y-%m-%d').date()
            return queryset.filter(created_at__date__gte=date_obj)
        except (ValueError, TypeError):
            return queryset

    class Meta:
        model = Post
        fields = ['title', 'author', 'created_after']
```

**Почему именно так:**
- ✅ `django-filter` — стандартный пакет для фильтрации в Django
- ✅ `method='filter_by_date'` — кастомная логика для работы с DateTimeField
- ✅ `created_at__date__gte` — сравнение по дате (игнорируя время и timezone)

**View:** `news/views.py`

```python
class PostSearch(FilterView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news'
    filterset_class = PostFilter
    paginate_by = 10
```

---

### 3.3 CRUD (Create, Read, Update, Delete)

**Файл:** `news/views.py`

```python
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
        # Автоматическая установка типа по URL
        if self.request.resolver_match.url_name == 'news_create':
            post.type = Post.NEWS
        elif self.request.resolver_match.url_name == 'article_create':
            post.type = Post.ARTICLE
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})

class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:post_list')
    
    def get_queryset(self):
        # Защита: удалять можно только свои посты
        return Post.objects.filter(author__user=self.request.user)
```

**Почему именно так:**
- ✅ `LoginRequiredMixin` — защита от неавторизованных пользователей
- ✅ `form_valid()` — автоматическая привязка автора и типа публикации
- ✅ `get_queryset()` в DeleteView — защита от удаления чужих постов

---

### 3.4 Аутентификация и авторизация

**Пакет:** `django-allauth`

**Настройки:** `pr_settings/settings.py`

```python
INSTALLED_APPS = [
    # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.yandex',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/news/'
LOGOUT_REDIRECT_URL = '/news/'
```

**Почему именно так:**
- ✅ `allauth` — готовая система аутентификации с социальными сетями
- ✅ `LOGIN_REDIRECT_URL` — куда перенаправлять после входа
- ✅ Yandex OAuth — удобная регистрация для пользователей из РФ

---

### 3.5 Группы и права доступа

| Группа | Права |
|--------|-------|
| `common` | Просмотр новостей и статей |
| `authors` | Создание и редактирование публикаций |

**Настройка прав в админке:**
1.  Admin → Authentication and Authorization → Groups
2.  Create Group `authors`
3.  Add Permissions: `news | post | Can add post`, `news | post | Can change post`

**Миксины прав в views:**

```python
from django.contrib.auth.mixins import PermissionRequiredMixin

class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'news.add_post'
    # ...

class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    # ...
```

---

### 3.6 Кастомные шаблонные фильтры

**Файл:** `news/templatetags/custom_filters.py`

```python
from django import template
import re

register = template.Library()

@register.filter
def censor(value):
    """Заменяет запрещённые слова на звёздочки"""
    if not value:
        return value
    bad_words = ['дурак', 'идиот', 'редиска', 'болван']
    result = value
    for word in bad_words:
        if len(word) > 2:
            censored = word[0] + '*' * (len(word) - 2) + word[-1]
        else:
            censored = '*' * len(word)
        result = re.sub(re.escape(word), censored, result, flags=re.IGNORECASE)
    return result

@register.filter
def remove(value, arg):
    """Удаляет параметр из QUERY_STRING (для пагинации)"""
    import urllib.parse
    params = urllib.parse.parse_qs(value)
    params.pop(arg, None)
    return urllib.parse.urlencode(params, doseq=True)
```

**Использование в шаблонах:**

```html
{% load custom_filters %}
<h1>{{ new.title|censor }}</h1>
<a href="?page={{ num }}&{{ request.GET.urlencode|remove:'page' }}">
```

---

## 4. Структура проекта

```
newsPortal/
├── .env                          # Переменные окружения (НЕ коммитить!)
├── .env.example                  # Шаблон переменных (можно коммитить)
├── .gitignore                    # Игнорируемые файлы
├── manage.py                     # Точка входа Django
├── requirements.txt              # Зависимости Python
├── db.sqlite3                    # База данных SQLite
├── pr_settings/
│   ├── __init__.py
│   ├── settings.py               # Настройки проекта
│   ├── urls.py                   # Корневые URL
│   └── wsgi.py                   # WSGI-конфигурация
├── news/
│   ├── __init__.py
│   ├── admin.py                  # Админ-панель
│   ├── apps.py
│   ├── filters.py                # Фильтры для поиска
│   ├── forms.py                  # Формы CRUD
│   ├── models.py                 # Модели данных
│   ├── urls.py                   # URL-маршруты news
│   ├── views.py                  # Представления (Views)
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── custom_filters.py     # Кастомные фильтры
│   └── migrations/
│       └── ...
├── accounts/
│   ├── __init__.py
│   ├── models.py                 # Модель Author
│   └── ...
├── templates/
│   ├── flatpages/
│   │   └── default.html          # Базовый шаблон
│   ├── account/
│   │   ├── login.html            # Вход
│   │   └── signup.html           # Регистрация
│   ├── news.html                 # Список новостей
│   ├── new.html                  # Детали новости
│   ├── news_search.html          # Поиск
│   ├── post_edit.html            # Создание/редактирование
│   └── post_delete.html          # Удаление
└── static/
    ├── css/
    ├── js/
    └── images/
```

---

## 5. Тестирование и проверка

### 5.1 Пагинация

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|--------|
| 1 | Открыть список новостей | `http://127.0.0.1:8000/news/` | Отображаются новости (макс. 10 на странице) | [📸](https://cloud.mail.ru/public/Qhoh/c1VTMDRUS) |
| 2 | Проверить пагинацию | Клик на `2` в пагинации | Страница 2, в URL `?page=2` | [📸](https://cloud.mail.ru/public/BRjh/MpFFVhVpk) |
| 3 | Перейти на последнюю | Клик на `Последняя »` | Последняя страница с новостями | [📸](https://cloud.mail.ru/public/BRjh/MpFFVhVpk) |
| 4 | Вернуться на первую | Клик на `« Первая` | Страница 1, `?page=1` | [📸](https://cloud.mail.ru/public/Qhoh/c1VTMDRUS)

---

### 5.2 Поиск и фильтрация

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|--------|
| 1 | Открыть поиск | `http://127.0.0.1:8000/news/search/` | Форма с 3 полями (Название, Автор, Дата) | [📸](https://cloud.mail.ru/public/2Vrp/zwH9KGp4W) |
| 2 | Поиск по названию | Ввести `Тест`, нажать Найти | Фильтрация по заголовку | [📸](https://cloud.mail.ru/public/Fttq/AHaqv3iJu) |
| 3 | Поиск по автору | Ввести `admin`, нажать Найти | Фильтрация по автору | [📸](https://cloud.mail.ru/public/NWd5/LJ4XAEwUr) |
| 4 | Поиск по дате | Выбрать `19.02.2026`, нажать Найти | Новости ≥ этой даты | [📸](https://cloud.mail.ru/public/RpCQ/SjYkcbKnG) |
| 5 | Комбинация фильтров | `Тест` + `admin` + дата | Все фильтры работают вместе | [📸](https://cloud.mail.ru/public/PDMH/wCngbEMzJ) |
| 6 | Пагинация с фильтрами | Клик на страницу 2 | Фильтры сохраняются в URL | [📸](https://cloud.mail.ru/public/mMuk/Zqgq2ugsx) |
| 7 | Сброс фильтров | Клик на `Сбросить` | Все новости без фильтров | [📸](https://cloud.mail.ru/public/EnYq/4GFYRvoLT) |

---

### 5.3 CRUD — Создание

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|--------|
| 1 | Форма создания новости | `http://127.0.0.1:8000/news/news/create/` | Форма (Заголовок, Текст, Категории) | [📸](https://cloud.mail.ru/public/kzGU/fr9BwYtuc) |
| 2 | Создать новость | Заполнить форму, Сохранить | Редирект на `/news/<pk>/` | [📸](https://cloud.mail.ru/public/eJwd/FBXfMc3vu) |
| 3 | Проверить тип | Открыть `/news/<pk>/` | Тип = `Новость` | [📸](https://cloud.mail.ru/public/a1aJ/sEzaqtWHN) |
| 4 | Форма создания статьи | `http://127.0.0.1:8000/news/articles/create/` | Та же форма | [📸](https://cloud.mail.ru/public/EJ3V/Wy94UFKdW) |
| 5 | Создать статью | Заполнить форму, Сохранить | Тип = `Статья` | [📸](https://cloud.mail.ru/public/ETgn/S46MCc2MZ) |
| 6 | Статья в списке | Открыть `/news/` | Статья НЕ отображается (только новости) | [📸](https://cloud.mail.ru/public/Gxeq/hoapRFDWo) |

---

### 5.4 CRUD — Редактирование

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|--------|
| 1 | Открыть редактирование | `http://127.0.0.1:8000/news/news/<pk>/edit/` | Форма с заполненными данными | [📸](https://cloud.mail.ru/public/pVki/4fmfK8eAG) |
| 2 | Изменить заголовок | Ввести новый, Сохранить | Заголовок обновлён | [📸](https://cloud.mail.ru/public/DRpE/BKLThFsBH) |
| 3 | Редактирование статьи | `http://127.0.0.1:8000/news/articles/<pk>/edit/` | Форма для статьи | [📸](https://cloud.mail.ru/public/xXpb/ik9QBkexa) |

---

### 5.5 CRUD — Удаление

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|--------|
| 1 | Открыть удаление | `http://127.0.0.1:8000/news/news/<pk>/delete/` | Страница подтверждения | [📸](https://cloud.mail.ru/public/bfJw/ZVuFAk7pY) |
| 2 | Подтвердить удаление | Клик `Да, удалить` | Редирект на `/news/`, пост удалён | [📸](https://cloud.mail.ru/public/8thP/DyfinNCe2) |
| 3 | Проверка в БД | `python manage.py shell` → `Post.objects.count()` | Количество уменьшилось на 1 | [📸](https://cloud.mail.ru/public/PuZK/daFhjCQM3) |

---

### 5.6 Аутентификация

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|----------|
| 1 | Страница входа | `http://127.0.0.1:8000/accounts/login/` | Форма входа + кнопка Yandex | [📸](#) |
| 2 | Вход по паролю | Ввести email/пароль | Редирект на `/news/` | [📸](#) |
| 3 | Вход через Yandex | Клик `Yandex` | OAuth Yandex → редирект на сайт | [📸](#) |
| 4 | Регистрация | `http://127.0.0.1:8000/accounts/signup/` | Форма регистрации | [📸](#) |
| 5 | Защита CRUD | Выйти, открыть `/news/news/create/` | Редирект на `/accounts/login/` | [📸](#) |

---

### 5.7 Права доступа (Группы)

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|----------|
| 1 | Создать группу common | Admin → Groups → Add | Группа `common` создана | [📸](#) |
| 2 | Создать группу authors | Admin → Groups → Add | Группа `authors` создана | [📸](#) |
| 3 | Настроить права authors | Add: `Can add post`, `Can change post` | Права назначены | [📸](#) |
| 4 | Добавить пользователя в authors | Admin → Users → Edit → Groups | Пользователь в группе | [📸](#) |
| 5 | Проверка прав | Войти как author, открыть create | Доступ есть | [📸](#) |
| 6 | Проверка прав | Войти как common, открыть create | Доступ запрещён (403 или редирект) | [📸](#) |

---

### 5.8 Автоматизированные тесты (Console)

```bash
# 1. Проверка миграций
python manage.py showmigrations

# 2. Проверка количества записей
python manage.py shell
>>> from news.models import Post
>>> Post.objects.count()
>>> Post.objects.filter(type='news').count()
>>> Post.objects.filter(type='article').count()

# 3. Проверка пользователей и групп
>>> from django.contrib.auth.models import User, Group
>>> User.objects.count()
>>> Group.objects.all()
>>> User.objects.get(username='admin').groups.all()

# 4. Проверка прав
>>> from news.models import Post
>>> user = User.objects.get(username='admin')
>>> user.has_perm('news.add_post')
>>> user.has_perm('news.change_post')
>>> user.has_perm('news.delete_post')

# 5. Проверка фильтра цензуры
>>> from news.templatetags.custom_filters import censor
>>> censor('Текст с плохим словом дурак')
'Текст с плохим словом д***к'
```

---

## 6. Зависимости

**Файл:** `requirements.txt`

```txt
Django==5.2.11
django-filter==24.3
django-allauth==65.0.2
python-decouple==3.8
requests==2.32.3
```

**Установка:**

```bash
pip install -r requirements.txt
```

---

## 7. Развёртывание

### 7.1 Локальный запуск

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env из шаблона
cp .env.example .env
# Отредактировать .env (SECRET_KEY, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET)

# 4. Применить миграции
python manage.py migrate

# 5. Создать суперпользователя
python manage.py createsuperuser

# 6. Запустить сервер
python manage.py runserver
```

### 7.2 Production (рекомендации)

| Настройка | Значение |
|-----------|----------|
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `['yourdomain.com', 'www.yourdomain.com']` |
| `DATABASE` | PostgreSQL вместо SQLite |
| `STATIC_ROOT` | `/var/www/static/` |
| `MEDIA_ROOT` | `/var/www/media/` |
| `SECRET_KEY` | Уникальный ключ (не из .env.example) |
| `HTTPS` | Обязательно (Let's Encrypt) |

---

## 📞 Контакты

**Разработчик:** Абрамов Андрей  
**Email:** npkap@mail.ru  
**Репозиторий:** https://github.com/andrzejabramov/news_portal.git

---

**© 2026 News Portal.**