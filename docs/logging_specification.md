# 📋 Отчет по заданию 4.1: Настройка системы логирования

## 1. Файловая структура проекта
```commandline
newsPortal/
├── pr_settings/
│ ├── init.py
│ ├── settings.py # Основные настройки + LOGGING конфигурация
│ ├── log_filters.py # Кастомные фильтры
│ ├── log_handlers.py # Кастомный обработчик для консоли
│ └── celery.py # Настройки Celery
│
├── news/
│ ├── management/
│ │ └── commands/
│ │ └── test_logging.py # Команда для тестирования логирования
│ └── ...
│
├── logs/ # Директория с лог-файлами
│ ├── general.log # Все INFO+ сообщения (только при DEBUG=False)
│ ├── errors.log # ERROR+ из django.request, server, template, db
│ └── security.log # Все сообщения из django.security
│
├── docs/
│ └── logging_specification.md # Документация
│
└── ...
```
### Графическое представление структуры:
``````
📁 newsPortal/
├── 📁 pr_settings/
│ ├── 📄 settings.py ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
│ ├── 📄 log_filters.py ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ┃
│ ├── 📄 log_handlers.py ◀━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃  ┃
│ └── 📄 celery.py                                 ┃ ┃  ┃
├── 📁 news/                                       ┃ ┃  ┃
│ └── 📁 management/                               ┃ ┃  ┃
│ └── 📁 commands/                                 ┃ ┃  ┃
│ └── 📄 test_logging.py ◀━━━━━━━━━━━━━━━━━------━━╋━╋━-╋┓
├── 📁 logs/                                       ┃ ┃  ┃┃
│ ├── 📄 general.log ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━╋━━╋┛
│ ├── 📄 errors.log ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━╋━━╋┓
│ └── 📄 security.log ◀━━━━━━━━━━━━━━━━━━━━━━━━━━━━╋━╋━━╋┛
└── 📁 docs/                                       ┃ ┃  ┃
└── 📄 logging_specification.md ◀━━━━━━━━━━━━━━━━━━┻━┻━━┛
``````

## 2. Взаимодействие между файлами

### Схема работы логирования:

```commandline
┌─────────────────────────────────────┐
│ Django Application                  │
│ (views.py, models.py, signals)      │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ Логгеры Django                      │
│ ┌─────────────-┐ ┌───────────---──┐ │
│ │ django       │ │ django.request │ │
│ │ django.server│ │ django.template│ │  
│ │ django.db    │ │ django.security│ │
│ └────────────-─┘ └───────────---──┘ │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ settings.py (LOGGING)               │
│ ┌─────────────┐ ┌─────────────┐     │
│ │ Filters     │ │ Formatters  │     │
│ │ (импорт из  │ │ (определены │     │
│ │ log_filters)│ │ в settings) │     │
│ └─────────────┘ └─────────────┘     │
│ ┌─────────────┐ ┌─────────────┐     │
│ │ Handlers    │ │ Loggers     │     │
│ │ (импорт из  │ │ (настройка  │     │
│ │log_handlers)│ │ маршрутов)  │     │
│ └─────────────┘ └─────────────┘     │
└────────────────────────┬────────────┘
                         │         
┌────────────────────────┼──────────────────────┐
▼                        ▼                      ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Консоль       │ │ Файлы логов   │ │ Email         │
│ (stdout)      │ │ general.log   │ │ ADMINS        │
│               │ │ errors.log    │ │               │
│               │ │ security.log  │ │               │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Назначение ключевых файлов:

| Файл | Назначение | Ключевые компоненты |
|------|------------|---------------------|
| **pr_settings/settings.py** | Основная конфигурация LOGGING | `LOGGING` dict с handlers, formatters, filters, loggers |
| **pr_settings/log_filters.py** | Кастомные фильтры | `DebugFilter`, `ProductionFilter`, `ErrorLogFilter`, `SecurityLogFilter` |
| **pr_settings/log_handlers.py** | Кастомные обработчики | `LevelBasedConsoleHandler` |
| **news/management/commands/test_logging.py** | Тестирование | Генерирует логи всех уровней |
| **logs/*.log** | Выходные файлы | Хранят отфильтрованные логи |

## 3. Запуск тестов

### Команды для тестирования:

```bash
# 1. Создать директорию для логов
mkdir -p logs

# 2. Запустить тест логирования
python manage.py test_logging

# 3. Проверить файлы логов
cat logs/errors.log
cat logs/security.log
cat logs/general.log

# 4. Проверить структуру
ls -la logs/
```
Ожидаемый вывод в консоль (при DEBUG=True):
```commandline
🧪 Тестирование логирования...
✅ Тестирование завершено!

2026-03-05 14:10:18 | INFO | test_logging | ℹ️ INFO сообщение
2026-03-05 14:10:18 | WARNING | test_logging | ⚠️ WARNING сообщение
2026-03-05 14:10:18 | ERROR | test_logging | ❌ ERROR сообщение
Traceback (most recent call last):
  File ".../test_logging.py", line 29, in handle
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```
Скриншоты выполнения:
(Здесь будут вставлены скриншоты)

Скриншот 1: Запуск теста в консоли

Скриншот 2: Содержимое errors.log

Скриншот 3: Содержимое security.log

Скриншот 4: Email-уведомление об ошибке

✅ Требование 1: Консольный вывод
Реализация:

Создан кастомный обработчик LevelBasedConsoleHandler

Разные форматы для разных уровней:

DEBUG/INFO: время | уровень | сообщение

WARNING+: время | уровень | pathname | сообщение

ERROR+: время | уровень | pathname | сообщение + exc_info

Фильтр debug_only - только при DEBUG=True

Код из log_handlers.py:
```commandline
class LevelBasedConsoleHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.formatters = {
            logging.DEBUG: logging.Formatter(
                '{asctime} | {levelname} | {message}',
                style='{', datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.INFO: logging.Formatter(
                '{asctime} | {levelname} | {message}',
                style='{', datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.WARNING: logging.Formatter(
                '{asctime} | {levelname} | {pathname} | {message}',
                style='{', datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.ERROR: logging.Formatter(
                '{asctime} | {levelname} | {pathname} | {message}\n{exc_info}',
                style='{', datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.CRITICAL: logging.Formatter(
                '{asctime} | {levelname} | {pathname} | {message}\n{exc_info}',
                style='{', datefmt='%Y-%m-%d %H:%M:%S'
            ),
        }
```
✅ Требование 2: Файл general.log
Реализация:

Уровень: INFO и выше

Формат: {asctime} | {levelname} | {module} | {message}

Фильтр production_only - только при DEBUG=False

Ротация файла (10 MB, 5 бэкапов)

Код из settings.py:
```commandline
'general_file': {
    'level': 'INFO',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(LOG_DIR, 'general.log'),
    'maxBytes': 10485760,  # 10 MB
    'backupCount': 5,
    'formatter': 'general',
    'filters': ['production_only'],
}
```
✅ Требование 3: Файл errors.log
Реализация:

Уровень: ERROR и CRITICAL

Только из логгеров: django.request, django.server, django.template, django.db.backends

Формат: {asctime} | {levelname} | {message} | {pathname}\n{exc_info}

Фильтр error_log_filter

Код из log_filters.py:
```commandline
class ErrorLogFilter(logging.Filter):
    allowed_loggers = {'django.request', 'django.server', 'django.template', 'django.db.backends'}
    
    def filter(self, record):
        logger_name_allowed = any(record.name.startswith(logger) for logger in self.allowed_loggers)
        level_allowed = record.levelno >= logging.ERROR
        return logger_name_allowed and level_allowed
```
✅ Требование 4: Файл security.log
Реализация:

Только из логгера django.security

Формат: {asctime} | {levelname} | {module} | {message}

Фильтр security_log_filter

Код из log_filters.py:
```commandline
class SecurityLogFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('django.security')
```
✅ Требование 5: Email для ошибок
Реализация:

Уровень: ERROR и выше

Только из логгеров: django.request, django.server

Формат: {asctime} | {levelname} | {message} | {pathname} (без exc_info)

Фильтр production_only - только при DEBUG=False

Настроены ADMINS

Код из settings.py:
```commandline
# Настройки email
ADMINS = [('Admin', 'admin@example.com')]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'your@yandex.ru'
EMAIL_HOST_PASSWORD = 'your-password'

# В LOGGING конфигурации
'mail_admins': {
    'level': 'ERROR',
    'class': 'django.utils.log.AdminEmailHandler',
    'formatter': 'email',
    'filters': ['production_only'],
}
```
✅ Требование 6: Фильтры по режиму DEBUG
Реализация:

debug_only: пропускает записи только при DEBUG=True

production_only: пропускает записи только при DEBUG=False

Код из log_filters.py:
```commandline
class DebugFilter(logging.Filter):
    def __init__(self):
        from django.conf import settings
        self.debug = settings.DEBUG
    
    def filter(self, record):
        return self.debug

class ProductionFilter(logging.Filter):
    def __init__(self):
        from django.conf import settings
        self.debug = settings.DEBUG
    
    def filter(self, record):
        return not self.debug
```
5. Результаты выполнения (отчет)
📊 Итоговая таблица выполнения
```commandline

№	Требование	Реализация	Статус
1	Консоль (DEBUG=True)	Разные форматы для разных уровней	✅
2	general.log (INFO+, DEBUG=False)	Время, уровень, модуль, сообщение	✅
3	errors.log (ERROR+, спец.логгеры)	Время, уровень, сообщение, pathname, exc_info	✅
4	security.log (django.security)	Время, уровень, модуль, сообщение	✅
5	Email (ERROR+, DEBUG=False)	Время, уровень, сообщение, pathname	✅
6	Фильтры DEBUG/production	debug_only / production_only	✅
```
При DEBUG=True:
```commandline
Канал	Результат	Причина
Консоль	✅ Все сообщения	debug_only пропускает
general.log	❌ Пустой	production_only блокирует
errors.log	✅ Ошибки от указанных логгеров	error_log_filter работает
security.log	✅ Сообщения безопасности	security_log_filter работает
Email	❌ Не отправляются	production_only блокирует

```
При DEBUG=False:
```commandline
Канал	Результат	Причина
Консоль	❌ Пустая	debug_only блокирует
general.log	✅ Все INFO+ сообщения	production_only пропускает
errors.log	✅ Ошибки от указанных логгеров	error_log_filter работает
security.log	✅ Сообщения безопасности	security_log_filter работает
Email	✅ Ошибки от request и server	production_only пропускает
```
📁 Созданные файлы логов
```commandline
logs/
├── general.log      # 0 байт (при DEBUG=True) / есть записи (при DEBUG=False)
├── errors.log       # ~700 байт (ошибки от специальных логгеров)
└── security.log     # ~180 байт (сообщения безопасности)
```
📧 Пример email-уведомления
```commandline
Content-Type: text/plain
Subject: [NewsPortal] ERROR (EXTERNAL IP): 🔥 Request error

2026-03-05 14:26:58 | ERROR | 🔥 Request error | /Users/.../test_logging.py

-------------------------------------------------------------------------------
Django Version: 5.2.11
Python Version: 3.11.11
Installed Applications:
['django.contrib.admin', 'django.contrib.auth', ...]
Installed Middleware:
['django.middleware.security.SecurityMiddleware', ...]
-------------------------------------------------------------------------------
```
🏆 Заключение
Задание 4.1 выполнено полностью! Все требования реализованы:

✅ Настроен многоуровневый вывод в консоль с разными форматами

✅ Создан файл general.log с INFO+ сообщениями (только в production)

✅ Создан файл errors.log с ERROR+ из указанных логгеров

✅ Создан файл security.log для сообщений безопасности

✅ Настроены email-уведомления об ошибках (только в production)

✅ Реализованы фильтры для DEBUG/production режимов

Система логирования полностью готова к использованию как в разработке, так и в продакшене.

Дата выполнения: 5 марта 2026
Исполнитель: Андрей Абрамов
Версия документа: 1.0
Статус: ✅ Завершено







