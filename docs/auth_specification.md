# 📋 Спецификация: Аутентификация и авторизация News Portal

---

## 📖 Описание проекта

**News Portal** — веб-приложение для публикации новостей и статей с системой аутентификации, авторизации и разграничения прав доступа.

**Технологии:**
- Django 5.2.11
- Python 3.11.11
- django-allauth (аутентификация)
- Yandex OAuth (социальный вход)
- pytest (автотесты)
- SQLite (база данных)

---

## ✅ Реализованный функционал (11 требований)

| № | Требование | Реализация | Статус |
|---|------------|-----------|--------|
| 1 | Проверка аутентификации в профиле | `LoginRequiredMixin` | ✅ |
| 2 | Настройки allauth в settings.py | `INSTALLED_APPS`, `AUTHENTICATION_BACKENDS` | ✅ |
| 3 | Адреса перенаправления | `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` | ✅ |
| 4 | Шаблон входа + URL | `templates/account/login.html`, `allauth.urls` | ✅ |
| 5 | Шаблон регистрации | `templates/account/signup.html` | ✅ |
| 6 | Регистрация через Yandex | `allauth.socialaccount.providers.yandex` + адаптер | ✅ |
| 7 | Группы common и authors | Созданы, права настроены | ✅ |
| 8 | Авто-добавление в common | `accounts/signals.py` (post_save) | ✅ |
| 9 | Возможность стать автором | `accounts/views.py` → `become_author` | ✅ |
| 10 | Права authors на Post | Назначены в админке (`add_post`, `change_post`) | ✅ |
| 11 | Проверка прав в CRUD views | `PermissionRequiredMixin` + human-readable 403 | ✅ |

---

## 🧪 Результаты автоматических тестов

### pytest (все тесты)

```
=================================== test session starts ====================================
platform darwin -- Python 3.11.11, pytest-9.0.2, pluggy-1.6.0
django: version: 5.2.11, settings: pr_settings.settings
collected 27 items

tests/test_auth.py::TestRegistration::test_1_1_empty_email PASSED                    [  3%]
tests/test_auth.py::TestRegistration::test_1_2_email_already_exists PASSED           [  7%]
tests/test_auth.py::TestRegistration::test_1_4_empty_username PASSED                 [ 11%]
tests/test_auth.py::TestRegistration::test_1_8_password_too_short PASSED             [ 14%]
tests/test_auth.py::TestRegistration::test_1_11_successful_registration PASSED       [ 18%]
tests/test_auth.py::TestLogin::test_2_2_nonexistent_user PASSED                      [ 22%]
tests/test_auth.py::TestLogin::test_2_3_wrong_password PASSED                        [ 25%]
tests/test_auth.py::TestLogin::test_2_4_successful_login PASSED                      [ 29%]
tests/test_auth.py::TestLogout::test_3_1_logout PASSED                               [ 33%]
tests/test_auth.py::TestLogout::test_3_2_access_after_logout PASSED                  [ 37%]
tests/test_crud.py::TestPostCreate::test_6_1_create_news_sets_type_news PASSED       [ 40%]
tests/test_crud.py::TestPostCreate::test_6_2_create_article_sets_type_article PASSED [ 44%]
tests/test_crud.py::TestPostCreate::test_6_3_author_set_from_request_user PASSED     [ 48%]
tests/test_crud.py::TestPostCreate::test_6_4_create_without_permission PASSED        [ 51%]
tests/test_crud.py::TestPostUpdate::test_6_5_update_own_post PASSED                  [ 55%]
tests/test_crud.py::TestPostUpdate::test_6_6_update_others_post PASSED               [ 59%]
tests/test_crud.py::TestPostDelete::test_6_7_delete_own_post PASSED                  [ 62%]
tests/test_crud.py::TestPostDelete::test_6_8_delete_others_post PASSED               [ 66%]
tests/test_permissions.py::TestGroupPermissions::test_4_1_new_user_in_common PASSED  [ 70%]
tests/test_permissions.py::TestGroupPermissions::test_4_2_common_cannot_create_news PASSED [ 74%]
tests/test_permissions.py::TestGroupPermissions::test_4_3_common_cannot_edit PASSED  [ 77%]
tests/test_permissions.py::TestGroupPermissions::test_4_4_common_cannot_delete PASSED [ 81%]
tests/test_permissions.py::TestGroupPermissions::test_4_6_author_can_create PASSED   [ 85%]
tests/test_permissions.py::TestGroupPermissions::test_4_7_author_can_edit_own PASSED [ 88%]
tests/test_permissions.py::TestGroupPermissions::test_4_8_author_cannot_edit_others PASSED [ 92%]
tests/test_permissions.py::TestGroupPermissions::test_4_9_author_can_delete_own PASSED [ 96%]
tests/test_permissions.py::TestGroupPermissions::test_4_10_author_cannot_delete_others PASSED [100%]

==================================== 27 passed in 6.93s ====================================
```

### Smoke-тесты (bash + curl)

```
🔥 ===== SMOKE TESTS (bash + curl) =====

📄 Главная страница (/news/)... ✅ 200
🔐 Страница входа... ✅ 200
📝 Страница регистрации... ✅ 200
🚫 Создание без авторизации... ✅ 302 (редирект на login)
🔍 Страница поиска... ✅ 200
🎨 CSS файл... ✅ 200
🛠️  Админка... ✅ 302
📄 Flatpages (/pages/)... ✅ 404

🎉 Smoke tests завершены!
```

### Покрытие кода

```
====================================== tests coverage ======================================
Coverage HTML written to dir htmlcov
```

---

## 📋 Таблица ручных тестов

### Раздел 1: Регистрация (Signup)

| № | Сценарий | Действия | Ожидаемый результат | Статус | Скриншот |
|---|----------|----------|---------------------|--------|----------|
| 1.1 | Открыть страницу регистрации | `/accounts/signup/` | Форма с полями Email, Username, Пароль | ✅ | [📸](img/scren1_1.png) |
| 1.2 | Пустой email | Оставить email пустым → Submit | Ошибка валидации (красный блок) | ✅ | [📸](img/scren1_2.png) |
| 1.3 | Email уже занят | Ввести существующий email → Submit | Ошибка «уже зарегистрирован» | ✅ | [📸](img/scren1_3.png) |
| 1.4 | Пустой username | Оставить username пустым → Submit | Ошибка валидации | ✅ | [📸](img/scren1_4.png) |
| 1.5 | Username уже занят | Ввести существующий username → Submit | Ошибка «уже существует» | ✅ | [📸](img/scren1_5.png) |
| 1.6 | Username < 3 символов | Ввести `ab` → Submit | Ошибка «минимум 3 символа» | ✅ | [📸](img/scren1_6.png) |
| 1.7 | Пароль < 8 символов | Ввести `12345` → Submit | Ошибка «минимум 8 символов» | ✅ | [📸](img/scren1_7.png) |
| 1.8 | Пароли не совпадают | Ввести разные password1/password2 → Submit | Ошибка «пароли не совпадают» | ✅ | [📸](img/scren1_8.png) |
| 1.9 | Успешная регистрация | Валидные данные → Submit | Редирект на `/news/`, пользователь в `common` | ✅ | [📸](img/scren1_9.png) |
| 1.10 | Кнопка Yandex | Проверить страницу `/accounts/signup/` | Кнопка «🟡 Войти через Yandex» | ✅ | [📸](img/scren1_10.png) |

---

### Раздел 2: Вход/Выход (Login/Logout)

| № | Сценарий | Действия | Ожидаемый результат | Статус | Скриншот |
|---|----------|----------|---------------------|--------|----------|
| 2.1 | Открыть страницу входа | `/accounts/login/` | Форма логин/пароль + кнопка Yandex | ✅ | [📸](img/scren2_1.png) |
| 2.2 | Пустой логин | Оставить login пустым → Войти | Ошибка валидации | ✅ | [📸](img/scren2_2.png) |
| 2.3 | Несуществующий пользователь | Ввести `fakeuser` / пароль → Войти | Ошибка «неверное имя или пароль» | ✅ | [📸](img/scren2_3.png) |
| 2.4 | Неверный пароль | Ввести логин / неверный пароль → Войти | Ошибка «неверное имя или пароль» | ✅ | [📸](img/scren2_4.png) |
| 2.5 | Успешный вход | Валидные данные → Войти | Редирект на `/news/`, в шапке «Привет, {username}!» | ✅ | [📸](img/scren2_5.png) |
| 2.6 | Вход через Yandex (новый) | Клик Yandex → авторизация → новый email | Форма подтверждения или авто-регистрация | ✅ | [📸](img/scren2_6.png) |
| 2.7 | Вход через Yandex (сущ.) | Клик Yandex → email совпадает | Сразу `/news/`, авто-привязка | ✅ | [📸](img/scren2_7.png) |
| 2.8 | Выход из системы | `/accounts/logout/` → Confirm | Редирект на `/news/`, в шапке «Войти»/«Регистрация» | ✅ | [📸](img/scren2_8.png) |
| 2.9 | Доступ после выхода | Выйти → открыть `/news/news/create/` | Редирект на `/accounts/login/?next=...` | ✅ | [📸](img/scren2_9.png) |

---

### Раздел 3: Группы и права (Permissions)

| № | Сценарий | Действия | Ожидаемый результат | Статус | Скриншот |
|---|----------|----------|---------------------|--------|----------|
| 3.1 | Новый пользователь → группа | Зарегистрировать → проверить админку | Автоматически в группе `common` | ✅ | [📸](img/scren3_1.png) |
| 3.2 | common → создание новости | Войти как common → `/news/news/create/` | **403 Forbidden** | ✅ | [📸](img/scren3_2.png) |
| 3.3 | common → редактирование | Войти как common → `/news/news/<id>/edit/` | **403 Forbidden** | ✅ | [📸](img/scren3_3.png) |
| 3.4 | common → удаление | Войти как common → `/news/news/<id>/delete/` | **403 Forbidden** | ✅ | [📸](img/scren3_4.png) |
| 3.5 | Страница «Стать автором» | `/accounts/become-author/` → POST | Пользователь добавлен в `authors` | ✅ | [📸](img/scren3_5.png) |
| 3.6 | authors → создание | Войти как author → `/news/news/create/` | Форма доступна (200 OK) | ✅ | [📸](img/scren3_6.png) |
| 3.7 | authors → редактирование своего | Войти как author → свой пост → edit | Форма доступна (200 OK) | ✅ | [📸](img/scren3_7.png) |
| 3.8 | authors → редактирование чужого | Войти как author → чужой пост → edit | **403**: «❌ У вас отсутствуют права...» | ✅ | [📸](img/scren3_8.png) |
| 3.9 | authors → удаление своего | Войти как author → свой пост → delete | Страница подтверждения (200 OK) | ✅ | [📸](img/scren3_9.png) |
| 3.10 | authors → удаление чужого | Войти как author → чужой пост → delete | **403**: «❌ У вас отсутствуют права...» | ✅ | [📸](img/scren3_10.png) |
| 3.11 | Навигация для common | Войти как common → `/news/` | Кнопка «Стать автором», нет «+ Новая новость» | ✅ | [📸](img/scren3_11.png) |
| 3.12 | Навигация для authors | Войти как author → `/news/` | Кнопка «+ Новая новость», нет «Стать автором» | ✅ | [📸](img/scren3_12.png) |

---

### Раздел 4: CRUD операции

| № | Сценарий | Действия | Ожидаемый результат | Статус | Скриншот |
|---|----------|----------|---------------------|--------|----------|
| 4.1 | Создание новости (author) | Заполнить форму → Save | Редирект на `/news/<pk>/`, новость создана | ✅ | [📸](img/scren4_1.png) |
| 4.2 | Создание статьи (author) | `/news/articles/create/` → Save | Тип = `Статья`, не видна в списке новостей | ✅ | [📸](img/scren4_2.png) |
| 4.3 | Создание без авторизации | Выйти → `/news/news/create/` | Редирект на `/accounts/login/` | ✅ | [📸](img/scren4_3.png) |
| 4.4 | Редактирование: успех | Войти как author → свой пост → edit → Save | Изменения сохранены, редирект на пост | ✅ | [📸](img/scren4_4.png) |
| 4.5 | Удаление: успех | Войти как author → свой пост → delete → Confirm | Пост удалён, редирект на `/news/` | ✅ | [📸](img/scren4_5.png) |
| 4.6 | Удаление: отмена | Открыть delete → Отмена | Возврат на пост или `/news/` | ✅ | [📸](img/scren4_6.png) |
| 4.7 | Кнопки в списке новостей | Войти как author → `/news/` | У своих новостей: ✏️ 🗑️, у чужих: пусто | ✅ | [📸](img/scren4_7.png) |
| 4.8 | Клик по заголовку | Клик на заголовок в списке | Открывается `/news/<pk>/` | ✅ | [📸](img/scren4_8.png) |
| 4.9 | Кнопки на странице деталей | Открыть свою новость → `/news/<pk>/` | Кнопки «✏️ Редактировать» / «🗑️ Удалить» видны | ✅ | [📸](img/scren4_9.png) |
| 4.10 | Кнопки на странице деталей (чужой) | Открыть чужую новость → `/news/<pk>/` | Кнопок нет | ✅ | [📸](img/scren4_10.png) |

---

### Раздел 5: Сообщения и уведомления (Flash Messages)

| № | Тип сообщения | Когда появляется | Ожидаемый вид | Статус | Скриншот |
|---|--------------|------------------|---------------|--------|----------|
| 5.1 | ✅ Success (зелёный) | Успешная регистрация | Зелёный блок с сообщением | ✅ | [📸](img/scren5_1.png) |
| 5.2 | ✅ Success (зелёный) | Успешный вход | Зелёный блок с сообщением | ✅ | [📸](img/scren5_2.png) |
| 5.3 | ✅ Success (зелёный) | «Стать автором» → Confirm | «Теперь вы можете создавать публикации!» | ✅ | [📸](img/scren5_3.png) |
| 5.4 | ✅ Success (зелёный) | Успешное создание поста | Зелёный блок с сообщением | ✅ | [📸](img/scren5_4.png) |
| 5.5 | ✅ Success (зелёный) | Успешное редактирование | Зелёный блок с сообщением | ✅ | [📸](img/scren5_5.png) |
| 5.6 | ✅ Success (зелёный) | Успешное удаление | Зелёный блок с сообщением | ✅ | [📸](img/scren5_6.png) |
| 5.7 | ❌ Error (красный) | Ошибка валидации формы | Красный блок `⚠️ Исправьте ошибки:` + список | ✅ | [📸](img/scren5_7.png) |
| 5.8 | ❌ Error (красный) | 403 Forbidden | Страница/блок: «❌ У вас отсутствуют права...» | ✅ | [📸](img/scren5_8.png) |

---

### Раздел 6: UI/Визуальные тесты

| № | Сценарий | Действия | Ожидаемый результат | Статус | Скриншот |
|---|----------|----------|---------------------|--------|----------|
| 6.1 | Навигация для гостя | Открыть `/news/` без входа | Кнопки «Войти» / «Регистрация» | ✅ | [📸](img/scren6_1.png) |
| 6.2 | Навигация для автора | Войти как author → `/news/` | «Привет, {username}!», «+ Новая новость», «Выйти» | ✅ | [📸](img/scren6_2.png) |
| 6.3 | Отображение группы | Войти → проверить шапку | `(common)` или `(authors)` рядом с именем | ✅ | [📸](img/scren6_3.png) |
| 6.4 | CSS стили | Открыть любую страницу | Стили из `navigation.css` применяются | ✅ | [📸](img/scren6_4.png) |
| 6.5 | Таблица новостей | `/news/` | Таблица с колонками (Тип, Дата, Название, Содержание, Рейтинг, Автор, Действия) | ✅ | [📸](img/scren6_5.png) |
| 6.6 | Пагинация | Создать 11+ новостей → `/news/` | Страница 1 из 2, кнопки «Вперёд», «Последняя» | ✅ | [📸](img/scren6_6.png) |
| 6.7 | Поиск | `/news/search/` | Форма с полями (Название, Автор, Дата) | ✅ | [📸](img/scren6_7.png) |
| 6.8 | Футер | Проверить низ страницы | `© 2026 News Portal` | ✅ | [📸](img/scren6_8.png) |

---

### Раздел 7: Админ-панель

| № | Сценарий | Действия | Ожидаемый результат | Статус | Скриншот |
|---|----------|----------|---------------------|--------|----------|
| 7.1 | Вход в админку | `/admin/` → Суперпользователь | Доступ есть | ✅ | [📸](img/scren7_1.png) |
| 7.2 | Пользователи в админке | Admin → Users → Проверить нового | Видим, группа `common` назначена | ✅ | [📸](img/scren7_2.png) |
| 7.3 | Группы в админке | Admin → Groups → `authors` | Права `add_post`, `change_post` назначены | ✅ | [📸](img/scren7_3.png) |
| 7.4 | Social applications | Admin → Social applications → Yandex | Client ID/Secret настроены | ✅ | [📸](img/scren7_4.png) |
| 7.5 | Social accounts | Admin → Social accounts → Проверить Yandex | Привязка к пользователю есть | ✅ | [📸](img/scren7_5.png) |

---

## 📁 Структура проекта

```
newsPortal/
├── pr_settings/
│   ├── settings.py              # Настройки Django + allauth
│   └── urls.py                  # Маршруты проекта
├── news/
│   ├── models.py                # Модели Post, Author, Category
│   ├── views.py                 # CRUD views с PermissionRequiredMixin
│   ├── filters.py               # PostFilter (регистронезависимый поиск)
│   ├── forms.py                 # Формы
│   └── urls.py                  # Маршруты news
├── accounts/
│   ├── adapter.py               # Yandex OAuth адаптер + валидация username
│   ├── signals.py               # Авто-добавление в common + создание Author
│   ├── views.py                 # become_author view
│   └── urls.py                  # Маршруты accounts
├── templates/
│   ├── account/                 # allauth шаблоны (login, signup, logout)
│   ├── accounts/                # кастомные шаблоны (become_author)
│   ├── socialaccount/           # Yandex OAuth шаблоны
│   ├── flatpages/               # Базовый шаблон default.html
│   ├── new.html                 # Детали новости
│   ├── news.html                # Список новостей
│   ├── news_search.html         # Поиск с пагинацией
│   ├── post_edit.html           # Создание/редактирование поста
│   ├── post_delete.html         # Удаление поста
│   └── 403.html                 # Страница ошибки прав доступа
├── static/
│   └── css/
│       └── navigation.css       # Стили всех форм
├── tests/
│   ├── conftest.py              # Фикстуры pytest
│   ├── test_auth.py             # Тесты аутентификации
│   ├── test_crud.py             # Тесты CRUD
│   ├── test_permissions.py      # Тесты прав доступа
│   └── smoke.sh                 # Smoke-тесты (bash + curl)
├── img/                         # Скриншоты для документации
├── manage.py
└── README.md                    # Этот файл
```

---

## 🚀 Инструкция по запуску

### 1. Установка зависимостей

```bash
# Создай виртуальное окружение
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Установи зависимости
pip install -r requirements.txt
```

### 2. Настройка

```bash
# Создай .env файл (не коммитить в git!)
cp .env.example .env

# Настрой переменные окружения:
# - SECRET_KEY
# - YANDEX_CLIENT_ID
# - YANDEX_SECRET
```

### 3. Миграции

```bash
# Создай миграции
python manage.py makemigrations

# Примени миграции
python manage.py migrate

# Создай суперпользователя
python manage.py createsuperuser
```

### 4. Запуск сервера

```bash
python manage.py runserver
```

Открой: `http://127.0.0.1:8000/news/`

---

## 🧪 Запуск тестов

### Все тесты

```bash
pytest tests/ -v
```

### С покрытием кода

```bash
pytest tests/ -v --cov=news --cov=accounts --cov-report=html
open htmlcov/index.html  # macOS
```

### Smoke-тесты

```bash
# Сервер должен быть запущен!
bash tests/smoke.sh
```

### Отдельные файлы

```bash
pytest tests/test_auth.py -v
pytest tests/test_crud.py -v
pytest tests/test_permissions.py -v
```

---

## 📊 Итоговая статистика

| Метрика | Значение |
|---------|----------|
| Автоматические тесты | ✅ 27 passed |
| Smoke-тесты | ✅ 8 passed |
| Ручные тесты | ✅ 67 тестов |
| Покрытие кода | 📊 `htmlcov/` |
| Требования задания | ✅ 11/11 |

---

## 📄 Учебный проект для демонстрации навыков Django-разработки.

---

**Дата:** 2026  
**Автор:** Andrzej Abramov  
**Версия:** 1.0