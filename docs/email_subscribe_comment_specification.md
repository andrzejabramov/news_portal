
markdown
# 📋 Спецификация: Email-уведомления, подписки и комментарии
## News Portal — Модуль взаимодействия с пользователем

## 🧭 Навигация по документу

| Действие | Как выполнить |
| :--- | :--- |
| 📸 **Открыть скриншот** | `Cmd+Click` (macOS) или `Ctrl+Click` (Windows/Linux) на иконке 📸 |
| 📸 **Альтернатива** | Правый клик → «Открыть в новой вкладке» |
| 🔙 **Вернуться к спецификации** | Используйте кнопку «Назад» в браузере (`Alt+←` или `Cmd+[`) |
| 📂 **Папка со скриншотами** | `/img/` в корне проекта |
| 📄 **Файл спецификации** | `docs/email_subscribe_comment_specification.md` |

---

## 1. 📧 Модуль почтовых уведомлений

### 1.1. Общая архитектура
*   **Библиотека:** `django-apscheduler` для периодических задач.
*   **Бэкенд:** Настраивается через переменные окружения (`.env`). Для разработки — консольный (`console`), для продакшна — SMTP (Яндекс).
*   **Шаблоны писем:** Находятся в `templates/emails/`. Есть HTML и текстовая версии для каждого типа писем.

### 1.2. Функционал

#### 1.2.1. Приветственное письмо
[Приветственное письмо]("../img/email_reg.png")
*   **Триггер:** Сигнал `post_save` на модели `User` (срабатывает при создании новой записи).
*   **Получатель:** Email, указанный пользователем при регистрации.
*   **Содержание:**
    *   Персонализированное приветствие с именем пользователя.
    *   Список ключевых возможностей портала.
    *   Прямая ссылка на каталог новостей (`/news/`).
*   **Обработка ошибок:** Логирование ошибок (если email не указан или SMTP недоступен). Регистрация пользователя происходит в любом случае.

#### 1.2.2. Мгновенное уведомление о новой публикации
*   **Триггеры:**
    1.  **Создание поста:** Сигнал `post_save` с `created=True`.
    2.  **Добавление категории:** Сигнал `m2m_changed` для связи `Post.categories.through`. Срабатывает при `action='post_add'`.
*   **Получатели:** Все пользователи с **активной** подпиской (`is_active=True`) на любую из категорий, к которым принадлежит новый пост.
*   **Содержание письма:**
    *   Заголовок публикации.
    *   Краткое содержание (первые 124 символа).
    *   Ссылка на полный текст статьи.
    *   Ссылка для отписки от данной категории.

#### 1.2.3. Еженедельный дайджест
*   **Периодичность:** Каждый понедельник в 09:00 утра (настраивается в `news/management/commands/runapscheduler.py`).
*   **Получатели:** Все пользователи, имеющие хотя бы одну активную подписку.
*   **Механизм работы:**
    1.  Собираются все посты, опубликованные за последние 7 дней.
    2.  Посты группируются по категориям.
    3.  Для каждого пользователя формируется персонализированное письмо, включающее только те категории, на которые он подписан.
*   **Содержание письма:**
    *   Приветствие.
    *   Список новых постов, сгруппированный по категориям.
    *   Для каждого поста: заголовок, автор, дата публикации, краткое содержание и ссылка для чтения.
*   **Команда для тестирования:** `python manage.py send_test_digest`

### 1.3. Настройки (`.env`)

```ini
# Режим отправки (console для разработки, smtp для продакшна)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Настройки SMTP (пример для Яндекс)
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your_login@yandex.ru
EMAIL_HOST_PASSWORD=your_app_password  # Пароль приложения, не основной!
DEFAULT_FROM_EMAIL=your_login@yandex.ru
SERVER_EMAIL=your_login@yandex.ru

# Префикс темы письма
EMAIL_SUBJECT_PREFIX=[NewsPortal]
```

### 1.4. Ручное тестирование (Email)
````
№	Сценарий	Действия	Ожидаемый результат	Статус	Скриншот
E1	Регистрация → приветственное письмо	Зарегистрировать нового пользователя с валидным email.	В консоли (или на почту) приходит письмо с приветствием и ссылкой на новости.	✅	📸
E2	Регистрация без email	Зарегистрировать нового пользователя, оставив поле email пустым.	Пользователь создается, письмо не отправляется, в логах ошибка.	✅	📸
E3	Новый пост → уведомление подписчику	1. Подписаться на категорию.
2. Создать пост в этой категории от имени автора.	Подписчик получает письмо с заголовком и ссылкой на новый пост.	✅	📸
E4	Новый пост → нет уведомления не подписчику	Создать пост в категории, на которую пользователь не подписан.	Пользователь не получает письмо.	✅	📸
E5	Ручной запуск дайджеста	Выполнить python manage.py send_test_digest.	В консоли появляются письма-дайджесты для всех подписчиков со списком постов за последние 7 дней.	✅	📸
E6	Дайджест: группировка по категориям	Создать посты в двух разных категориях, на которые подписан пользователь. Запустить дайджест.	В письме посты сгруппированы под заголовками соответствующих категорий.	✅	📸
E7	Дайджест не уходит отписавшимся	Отписаться от категории, создать в ней пост, запустить дайджест.	Письмо с этим постом не приходит бывшему подписчику.	✅	📸
2. 🔔 Модуль подписок на категории
````
### 2.1. Модель данных
Модель: UserCategorySubscription в news/models.py.

Поля:

user (ForeignKey на User)
category (ForeignKey на Category)
created_at (DateTimeField)
is_active (BooleanField, default=True) — для "мягкой" отписки.
Уникальность: unique_together = ('user', 'category') — гарантирует одну подписку на пару пользователь-категория.

### 2.2. API (View)
SubscribeToggleView (/news/subscribe/<int:category_pk>/):
Обрабатывает POST-запросы от форм.
Аргумент action (subscribe/unsubscribe) определяет действие.
При успехе показывает всплывающее сообщение (django.contrib.messages).
Доступно только авторизованным пользователям (LoginRequiredMixin).
SubscriptionsListView (/news/subscriptions/):
Страница со списком всех категорий.
Для каждой категории отображается статус подписки текущего пользователя и кнопка для переключения.

### 2.3. Интерфейс пользователя (UI)

Шаблонный тег: {% check_subscription user.id category.id %} (из subscription_tags.py) для проверки статуса подписки прямо в шаблоне.
Кнопка подписки: Вынесена в отдельный файл templates/news/_subscribe_button.html для переиспользования.
Расположение кнопок:
В общем списке новостей (news.html): рядом с названием каждой категории поста.
На детальной странице поста (new.html): в отдельном блоке "📁 Категории", где каждая категория выводится в паре со своей кнопкой.

### 2.4. Ручное тестирование (Подписки)
```
№	Сценарий	Действия	Ожидаемый результат	Статус	Скриншот
S1	Кнопка для гостя	Открыть любую страницу с категориями будучи неавторизованным.	Видна кнопка «🔔 Войти для подписки».	✅	📸
S2	Подписка через кнопку (POST)	Авторизоваться. Нажать «🔔 Подписаться» у любой категории.	1. Появляется сообщение «✅ Вы подписаны...».
2. Кнопка меняется на «🔕 Отписаться».	✅	📸
S3	Отписка через кнопку (POST)	Нажать «🔕 Отписаться» у категории, на которую подписан.	1. Появляется сообщение «🔕 Вы отписались...».
2. Кнопка меняется на «🔔 Подписаться».	✅	📸
S4	Страница управления подписками	Перейти по ссылке «📁 Мои подписки» в меню.	Открывается страница со списком всех категорий. У каждой указан статус и кнопка.	✅	📸
S5	Подписка/отписка через общую страницу	На странице /news/subscriptions/ нажать кнопку для любой категории.	Действие выполняется, статус и кнопка обновляются после перезагрузки страницы.	✅	📸
S6	Проверка БД после подписки	Выполнить UserCategorySubscription.objects.filter(user=user, category=category, is_active=True) в shell.	Запись существует с is_active=True.	✅	📸
S7	Проверка БД после отписки	Выполнить ту же команду после отписки.	Запись существует с is_active=False.	✅	📸
```
## 3. 💬 Модуль комментариев
### 3.1. Модель данных

Модель: Comment в news/models.py.

Поля:

post (ForeignKey на Post, on_delete=models.CASCADE)
user (ForeignKey на User, on_delete=models.CASCADE)
text (TextField)
created_at (DateTimeField, auto_now_add=True)
rating (IntegerField, default=0)

### 3.2. Функционал

Добавление комментария (add_comment): Доступно только авторизованным пользователям. Форма находится на странице поста.
Редактирование комментария (edit_comment): Доступно только автору комментария. (Опционально: временное ограничение, например, в течение 30 минут после публикации).
Удаление комментария (delete_comment): Доступно только автору комментария.
Голосование (лайк/дизлайк): Отдельные view (like_comment, dislike_comment) для изменения рейтинга комментария. Доступно только авторизованным.
Отображение: Комментарии под постом отображаются в порядке убывания даты создания (сначала новые). Реализована пагинация (например, по 20 комментариев на странице).

### 3.3. Ручное тестирование (Комментарии)
````
№	Сценарий	Действия	Ожидаемый результат	Статус	Скриншот
C1	Добавление комментария (авторизован)	Открыть пост, ввести текст в форму, нажать "Отправить".	Комментарий появляется под постом, указаны автор и время.	✅	📸
C2	Добавление комментария (гость)	Будучи неавторизованным, попытаться отправить комментарий.	Редирект на страницу входа.	✅	📸
C3	Добавление пустого комментария	Авторизоваться, нажать "Отправить", оставив поле пустым.	Форма не отправляется (валидация на стороне клиента или сервера).	✅	📸
C4	Редактирование своего комментария	Авторизоваться под автором комментария, нажать "Редактировать", изменить текст, сохранить.	Текст комментария обновляется.	✅	📸
C5	Редактирование чужого комментария	Авторизоваться под другим пользователем, попытаться отредактировать чужой комментарий.	Действие недоступно (кнопка не видна или возвращается 403).	✅	📸
C6	Удаление своего комментария	Авторизоваться под автором, нажать "Удалить", подтвердить.	Комментарий исчезает со страницы.	✅	📸
C7	Удаление чужого комментария	Авторизоваться под другим пользователем, попытаться удалить чужой комментарий.	Действие недоступно (кнопка не видна или возвращается 403).	✅	📸
C8	Лайк комментария	Авторизоваться, нажать "👍" под комментарием.	Рейтинг комментария увеличивается на 1.	✅	📸
C9	Дизлайк комментария	Авторизоваться, нажать "👎" под комментарием.	Рейтинг комментария уменьшается на 1.	✅	📸
C10	Повторный лайк/дизлайк	Поставить лайк, потом дизлайк.	Рейтинг сначала +1, потом -1. (Здесь можно описать более сложную логику, если она есть, например, отмена голоса)	✅	📸
C11	Голосование гостем	Будучи неавторизованным, нажать "👍" или "👎".	Редирект на страницу входа.	✅	📸
C12	Пагинация комментариев	Создать >20 комментариев к одному посту. Открыть пост.	Видны первые 20 комментариев и элементы навигации по страницам.	✅	📸
C13	Порядок комментариев	Создать несколько комментариев с разницей во времени.	Самый новый комментарий отображается первым (сверху).	✅	📸
````
## 4. 🧪 Автоматические тесты (pytest)

Все новые функции покрыты тестами. Результат прогона всех 66 тестов:

bash
collected 66 items
`````
... (список всех тестов) ...

============================ 66 passed, 2 warnings in 15.87s =============================
`````

## 5. ⚙️ Запуск и обслуживание
### 5.1. Запуск планировщика
Для работы еженедельных рассылок необходимо запустить отдельный процесс с планировщиком:

```bash
python manage.py runapscheduler
```
В production-среде этот процесс должен управляться supervisor или systemd.

### 5.2. Production-переменные (.env)
text

# Переключение с консоли на реальный SMTP
````
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# ... остальные настройки SMTP ...
````

### 5.3. Известные ограничения и TODO

[[#DELETE-001]]: Заменить заглушки удаления в urls.py на реальные PostDelete view. (См. TODO.md)

[[#EMAIL-001]]: Добавить больше шаблонов для разных типов уведомлений (например, об ответе на комментарий).
````bash
(venv) andrejabramov@192 newsPortal % pytest tests/ -v
========================================================================= test session starts =========================================================================
platform darwin -- Python 3.11.11, pytest-9.0.2, pluggy-1.6.0 -- /Users/andrejabramov/Desktop/Urban/newsPortal/venv/bin/python3
cachedir: .pytest_cache
django: version: 5.2.11, settings: pr_settings.settings (from ini)
rootdir: /Users/andrejabramov/Desktop/Urban/newsPortal
configfile: pytest.ini
plugins: django-4.12.0, cov-7.0.0
collected 66 items                                                                                                                                                    

tests/test_auth.py::TestRegistration::test_1_1_empty_email PASSED                                                                                               [  1%]
tests/test_auth.py::TestRegistration::test_1_2_email_already_exists PASSED                                                                                      [  3%]
tests/test_auth.py::TestRegistration::test_1_4_empty_username PASSED                                                                                            [  4%]
tests/test_auth.py::TestRegistration::test_1_8_password_too_short PASSED                                                                                        [  6%]
tests/test_auth.py::TestRegistration::test_1_11_successful_registration PASSED                                                                                  [  7%]
tests/test_auth.py::TestLogin::test_2_2_nonexistent_user PASSED                                                                                                 [  9%]
tests/test_auth.py::TestLogin::test_2_3_wrong_password PASSED                                                                                                   [ 10%]
tests/test_auth.py::TestLogin::test_2_4_successful_login PASSED                                                                                                 [ 12%]
tests/test_auth.py::TestLogout::test_3_1_logout PASSED                                                                                                          [ 13%]
tests/test_auth.py::TestLogout::test_3_2_access_after_logout PASSED                                                                                             [ 15%]
tests/test_comments.py::TestAddComment::test_6_1_add_comment_authenticated PASSED                                                                               [ 16%]
tests/test_comments.py::TestAddComment::test_6_2_add_comment_sets_user PASSED                                                                                   [ 18%]
tests/test_comments.py::TestAddComment::test_6_3_add_comment_sets_post PASSED                                                                                   [ 19%]
tests/test_comments.py::TestAddComment::test_6_4_add_comment_guest_redirects PASSED                                                                             [ 21%]
tests/test_comments.py::TestAddComment::test_6_5_add_comment_empty_text PASSED                                                                                  [ 22%]
tests/test_comments.py::TestEditComment::test_6_6_edit_comment_own PASSED                                                                                       [ 24%]
tests/test_comments.py::TestEditComment::test_6_7_edit_comment_others_403 PASSED                                                                                [ 25%]
tests/test_comments.py::TestEditComment::test_6_8_edit_comment_shows_form PASSED                                                                                [ 27%]
tests/test_comments.py::TestDeleteComment::test_6_9_delete_comment_own PASSED                                                                                   [ 28%]
tests/test_comments.py::TestDeleteComment::test_6_10_delete_comment_others_403 PASSED                                                                           [ 30%]
tests/test_comments.py::TestCommentRating::test_6_11_like_increments_rating PASSED                                                                              [ 31%]
tests/test_comments.py::TestCommentRating::test_6_12_dislike_decrements_rating PASSED                                                                           [ 33%]
tests/test_comments.py::TestCommentRating::test_6_13_like_guest_redirects PASSED                                                                                [ 34%]
tests/test_comments.py::TestCommentRating::test_6_14_dislike_guest_redirects PASSED                                                                             [ 36%]
tests/test_comments.py::TestCommentDisplay::test_6_15_comments_ordered_by_created_at PASSED                                                                     [ 37%]
tests/test_crud.py::TestPostCreate::test_6_1_create_news_sets_type_news PASSED                                                                                  [ 39%]
tests/test_crud.py::TestPostCreate::test_6_2_create_article_sets_type_article PASSED                                                                            [ 40%]
tests/test_crud.py::TestPostCreate::test_6_3_author_set_from_request_user PASSED                                                                                [ 42%]
tests/test_crud.py::TestPostCreate::test_6_4_create_without_permission PASSED                                                                                   [ 43%]
tests/test_crud.py::TestPostUpdate::test_6_5_update_own_post PASSED                                                                                             [ 45%]
tests/test_crud.py::TestPostUpdate::test_6_6_update_others_post PASSED                                                                                          [ 46%]
tests/test_crud.py::TestPostDelete::test_6_7_delete_own_post PASSED                                                                                             [ 48%]
tests/test_crud.py::TestPostDelete::test_6_8_delete_others_post PASSED                                                                                          [ 50%]
tests/test_email.py::TestWelcomeEmail::test_7_1_send_welcome_email_renders PASSED                                                                               [ 51%]
tests/test_email.py::TestWelcomeEmail::test_7_2_send_welcome_email_contains_username PASSED                                                                     [ 53%]
tests/test_email.py::TestWelcomeEmail::test_7_3_send_welcome_email_skips_no_email PASSED                                                                        [ 54%]
tests/test_email.py::TestNewPostNotification::test_7_4_send_new_post_notification_to_subscribers PASSED                                                         [ 56%]
tests/test_email.py::TestNewPostNotification::test_7_5_signal_triggers_on_post_create PASSED                                                                    [ 57%]
tests/test_email.py::TestNewPostNotification::test_7_6_notification_sent_only_to_subscribers PASSED                                                             [ 59%]
tests/test_email.py::TestWeeklyDigest::test_7_7_send_weekly_digest_includes_recent_posts PASSED                                                                 [ 60%]
tests/test_email.py::TestWeeklyDigest::test_7_8_send_weekly_digest_groups_by_category PASSED                                                                    [ 62%]
tests/test_email.py::TestWeeklyDigest::test_7_9_send_weekly_digest_skips_unsubscribed PASSED                                                                    [ 63%]
tests/test_email.py::TestEmailBackend::test_7_10_email_uses_console_backend_in_tests PASSED                                                                     [ 65%]
tests/test_email.py::TestEmailBackend::test_7_11_mail_outbox_accessible PASSED                                                                                  [ 66%]
tests/test_permissions.py::TestGroupPermissions::test_4_1_new_user_in_common PASSED                                                                             [ 68%]
tests/test_permissions.py::TestGroupPermissions::test_4_2_common_cannot_create_news PASSED                                                                      [ 69%]
tests/test_permissions.py::TestGroupPermissions::test_4_3_common_cannot_edit PASSED                                                                             [ 71%]
tests/test_permissions.py::TestGroupPermissions::test_4_4_common_cannot_delete PASSED                                                                           [ 72%]
tests/test_permissions.py::TestGroupPermissions::test_4_6_author_can_create PASSED                                                                              [ 74%]
tests/test_permissions.py::TestGroupPermissions::test_4_7_author_can_edit_own PASSED                                                                            [ 75%]
tests/test_permissions.py::TestGroupPermissions::test_4_8_author_cannot_edit_others PASSED                                                                      [ 77%]
tests/test_permissions.py::TestGroupPermissions::test_4_9_author_can_delete_own PASSED                                                                          [ 78%]
tests/test_permissions.py::TestGroupPermissions::test_4_10_author_cannot_delete_others PASSED                                                                   [ 80%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_1_subscribe_creates_subscription PASSED                                                            [ 81%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_2_subscribe_sets_is_active_true PASSED                                                             [ 83%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_3_unsubscribe_sets_is_active_false PASSED                                                          [ 84%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_4_subscribe_shows_success_message PASSED                                                           [ 86%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_5_unsubscribe_shows_success_message PASSED                                                         [ 87%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_6_guest_cannot_subscribe PASSED                                                                    [ 89%]
tests/test_subscriptions.py::TestSubscribeToggleView::test_5_7_subscribe_via_get_method PASSED                                                                  [ 90%]
tests/test_subscriptions.py::TestSubscriptionsListView::test_5_8_subscriptions_list_shows_all_categories PASSED                                                 [ 92%]
tests/test_subscriptions.py::TestSubscriptionsListView::test_5_9_subscriptions_list_shows_status PASSED                                                         [ 93%]
tests/test_subscriptions.py::TestSubscriptionsListView::test_5_10_guest_cannot_view_subscriptions PASSED                                                        [ 95%]
tests/test_subscriptions.py::TestSubscriptionTemplateTag::test_5_11_check_subscription_returns_true PASSED                                                      [ 96%]
tests/test_subscriptions.py::TestSubscriptionTemplateTag::test_5_12_check_subscription_returns_false PASSED                                                     [ 98%]
tests/test_subscriptions.py::TestSubscriptionTemplateTag::test_5_13_check_subscription_returns_false_inactive PASSED                                            [100%]

=================================================================== 66 passed, 2 warnings in 15.38s ===================================================================
(venv) andrejabramov@192 newsPortal % 
````
