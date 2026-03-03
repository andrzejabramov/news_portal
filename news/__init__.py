# news/__init__.py

# Явно указываем AppConfig для приложения news
# Это гарантирует, что метод ready() будет вызван
default_app_config = 'news.apps.NewsConfig'
