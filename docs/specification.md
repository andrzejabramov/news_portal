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

#### 🔹 Требование 1: Проверка аутентификации в редактировании профиля

**Файл:** `accounts/views.py` (или кастомный view профиля)

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

class ProfileUpdate(LoginRequiredMixin, UpdateView):
    """Редактирование профиля — только для авторизованных"""
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'account/profile_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('news:post_list')
```

> ✅ `LoginRequiredMixin` автоматически редиректит неавторизованных на `/accounts/login/`

---

#### 🔹 Требование 2: Настройки allauth в settings.py

**Файл:** `pr_settings/settings.py`

```python
INSTALLED_APPS = [
    # ... стандартные ...
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.yandex',  # ← Провайдер Yandex
]

SITE_ID = 1  # ← Обязательно для allauth

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Стандартная аутентификация
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth
]

# Настройки allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Для разработки; в продакшене: 'mandatory'
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']

# Yandex OAuth
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_AUTO_SIGNUP = True
```

---

#### 🔹 Требование 3: Редиректы после входа/выхода

**Файл:** `pr_settings/settings.py` (в конце)

```python
# Адреса перенаправления
LOGIN_URL = '/accounts/login/'           # Куда при попытке доступа без авторизации
LOGIN_REDIRECT_URL = '/news/'            # Куда после успешного входа
LOGOUT_REDIRECT_URL = '/news/'           # Куда после выхода
```

---

#### 🔹 Требование 4: Шаблон входа + URL-конфигурация

**Шаблон:** `templates/account/login.html` (создаётся автоматически allauth, можно кастомизировать)

```html
{% extends 'flatpages/default.html' %}
{% load socialaccount %}

{% block content %}
<h2>Вход в систему</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Войти</button>
</form>

<p><a href="{% url 'account_signup' %}">Нет аккаунта? Зарегистрироваться</a></p>

<hr>
<p><strong>Войти через:</strong></p>
<a href="{% provider_login_url 'yandex' %}" class="btn btn-yandex">
    🟡 Yandex
</a>
{% endblock %}
```

**URL-конфигурация:** `pr_settings/urls.py`

```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    
    # Allauth URLs (обязательно!)
    path('accounts/', include('allauth.urls')),
]
```

---

#### 🔹 Требование 5: Шаблон регистрации

**Шаблон:** `templates/account/signup.html`

```html
{% extends 'flatpages/default.html' %}

{% block content %}
<h2>Регистрация</h2>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-success">Зарегистрироваться</button>
</form>

<p><a href="{% url 'account_login' %}">Уже есть аккаунт? Войти</a></p>
{% endblock %}
```

> 💡 Allauth автоматически создаёт пользователя и добавляет его в группу `common` (через signals).

---

#### 🔹 Требование 6: Регистрация через Yandex

**Настройка SocialApp в админке:**

1.  Admin → **Social applications** → Add
2.  Provider: `Yandex`
3.  Name: `Yandex OAuth`
4.  Client ID: `из кабинета https://oauth.yandex.ru/client/`
5.  Secret key: `из кабинета`
6.  Sites: выбрать `example.com` → добавить в «Выбранные»

**Кнопка в шаблоне входа** (см. Требование 4):

```html
<a href="{% provider_login_url 'yandex' %}">🟡 Войти через Yandex</a>
```

**Адаптер для авто-привязки** (опционально, но рекомендуется): `accounts/adapter.py`

```python
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class AutoConnectSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Авто-привязка Yandex к существующему пользователю по email"""
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
        
        email = None
        if sociallogin.account and sociallogin.account.extra_
            data = sociallogin.account.extra_data
            email = data.get('email') or data.get('default_email')
            if not email and isinstance(data.get('emails'), list) and data['emails']:
                email = data['emails'][0]
        
        if not email:
            return
        
        User = get_user_model()
        try:
            user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, user)
            logger.debug(f"✅ Connected Yandex to {user.username}")
        except User.DoesNotExist:
            pass  # Создастся новый пользователь (стандартное поведение)
```

**Подключение адаптера:** `pr_settings/settings.py`

```python
SOCIALACCOUNT_ADAPTER = 'accounts.adapter.AutoConnectSocialAccountAdapter'
```

---

#### 🔹 Требование 7: Группы common и authors

**Создание через админку:**

1.  Admin → **Groups** → Add Group
2.  Name: `common` → Save
3.  Add Group → Name: `authors` → Save

**Или через shell:**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group

common, _ = Group.objects.get_or_create(name='common')
authors, _ = Group.objects.get_or_create(name='authors')
print(f"✅ Группы созданы: {common}, {authors}")
```

---

#### 🔹 Требование 8: Авто-добавление в группу common

**Файл:** `accounts/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

@receiver(post_save, sender=User)
def add_to_common_group(sender, instance, created, **kwargs):
    """Автоматически добавлять новых пользователей в группу common"""
    if created:
        common_group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(common_group)
```

**Подключение сигнала:** `accounts/apps.py`

```python
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals  # ← Регистрация сигналов
```

---

#### 🔹 Требование 9: Страница «Стать автором»

**View:** `accounts/views.py`

```python
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def become_author(request):
    """Заявка на добавление в группу authors"""
    if request.method == 'POST':
        authors_group = Group.objects.get(name='authors')
        request.user.groups.add(authors_group)
        messages.success(request, '✅ Вы теперь автор! Можете создавать новости.')
        return redirect('news:post_list')
    return render(request, 'accounts/become_author.html')
```

**Шаблон:** `templates/accounts/become_author.html`

```html
{% extends 'flatpages/default.html' %}

{% block content %}
<h2>Стать автором</h2>
<p>Вы хотите получить возможность создавать и редактировать новости?</p>

<form method="post">
    {% csrf_token %}
    <button type="submit" class="btn btn-primary">Да, стать автором</button>
</form>
<a href="{% url 'news:post_list' %}">← Отмена</a>
{% endblock %}
```

**URL:** `accounts/urls.py`

```python
from django.urls import path
from .views import become_author

app_name = 'accounts'

urlpatterns = [
    path('become-author/', become_author, name='become_author'),
]
```

---

#### 🔹 Требование 10: Права для группы authors на Post

**Настройка через админку:**

1.  Admin → **Groups** → `authors` → Edit
2.  Раздел **Permissions** → Available permissions:
    -   ✅ `news | post | Can add post`
    -   ✅ `news | post | Can change post`
3.  Перенести в **Chosen permissions** → Save

**Или через shell:**

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Post

authors = Group.objects.get(name='authors')
content_type = ContentType.objects.get_for_model(Post)

add_perm = Permission.objects.get(content_type=content_type, codename='add_post')
change_perm = Permission.objects.get(content_type=content_type, codename='change_post')

authors.permissions.add(add_perm, change_perm)
print("✅ Права назначены группе authors")
```

---

#### 🔹 Требование 11: Проверка прав в CRUD-views

**Файл:** `news/views.py`

```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """Создание новости/статьи — только для authors"""
    permission_required = 'news.add_post'  # ← Проверка права
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
        if self.request.resolver_match.url_name == 'news_create':
            post.type = Post.NEWS
        elif self.request.resolver_match.url_name == 'article_create':
            post.type = Post.ARTICLE
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('news:post_detail', kwargs={'pk': self.object.pk})

class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    """Редактирование — только для authors"""
    permission_required = 'news.change_post'  # ← Проверка права
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    
    def get_queryset(self):
        # Дополнительно: разрешать редактировать только свои посты
        return Post.objects.filter(author__user=self.request.user)
```

> 🔐 При отсутствии права пользователь получит **403 Forbidden** (или можно добавить `raise_exception=False` для редиректа).
```

---

### 2. Добавить таблицы тестирования аутентификации (в раздел 5)

```markdown
### 5.6 Аутентификация и авторизация

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|----------|
| 1 | Страница входа | `http://127.0.0.1:8000/accounts/login/` | Форма входа + кнопка Yandex | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 2 | Вход по паролю | Ввести email/пароль → Войти | Редирект на `/news/`, в шапке «Привет, {username}!» | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 3 | Вход через Yandex | Клик `🟡 Yandex` → авторизация в Яндексе | Редирект на `/news/`, пользователь авторизован | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 4 | Страница регистрации | `http://127.0.0.1:8000/accounts/signup/` | Форма регистрации (email, username, пароль) | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 5 | Регистрация нового пользователя | Заполнить форму → Зарегистрироваться | Создан пользователь, добавлен в группу `common`, редирект на `/news/` | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 6 | Защита CRUD без авторизации | Выйти, открыть `/news/news/create/` | Редирект на `/accounts/login/?next=/news/news/create/` | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 7 | Группа common — нет прав на создание | Войти как common, открыть `/news/news/create/` | 403 Forbidden или редирект | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 8 | Группа authors — есть права | Войти как author, открыть `/news/news/create/` | Форма создания новости доступна | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 9 | Страница «Стать автором» | `/accounts/become-author/` → Подтвердить | Пользователь добавлен в группу `authors` | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
|10| Проверка прав в БД | `shell` → `user.groups.all()` | У автора есть группа `authors` | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
|11| Выход из системы | `/accounts/logout/` → Подтвердить | Редирект на `/news/`, в шапке кнопки «Войти»/«Регистрация» | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
```

> 💡 **Замени ссылки `[📸](https://cloud.mail.ru/public/XXXX/XXXX)` на реальные ссылки из твоего облака.**

---

### 3. Обновить раздел **5.7 Права доступа (Группы)** (опционально)

```markdown
### 5.7 Права доступа (Группы)

| № | Проверка | Команда / URL | Ожидаемый результат | Скриншот |
|---|----------|---------------|---------------------|----------|
| 1 | Создать группу common | Admin → Groups → Add | Группа `common` создана | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 2 | Создать группу authors | Admin → Groups → Add | Группа `authors` создана | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 3 | Настроить права authors | Add: `Can add post`, `Can change post` | Права назначены | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 4 | Авто-добавление в common | Зарегистрировать нового пользователя | В админке: пользователь в группе `common` | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 5 | Заявка «Стать автором» | `/accounts/become-author/` → Подтвердить | Пользователь в группе `authors` | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 6 | Проверка прав на создание | Войти как author → `/news/news/create/` | Доступ разрешён | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
| 7 | Проверка прав без authors | Войти как common → `/news/news/create/` | Доступ запрещён (403) | [📸](https://cloud.mail.ru/public/XXXX/XXXX) |
```


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