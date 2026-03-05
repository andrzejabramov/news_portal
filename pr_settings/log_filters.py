import logging


class DebugFilter(logging.Filter):
    """
    Пропускает записи только когда DEBUG = True
    """

    def __init__(self):
        # Импортируем здесь, чтобы избежать циклических импортов
        from django.conf import settings
        self.debug = settings.DEBUG

    def filter(self, record):
        return self.debug


class ProductionFilter(logging.Filter):
    """
    Пропускает записи только когда DEBUG = False
    """

    def __init__(self):
        from django.conf import settings
        self.debug = settings.DEBUG

    def filter(self, record):
        return not self.debug


class ErrorLogFilter(logging.Filter):
    """
    Фильтр для errors.log: только ERROR и CRITICAL из указанных логгеров
    """
    allowed_loggers = {'django.request', 'django.server', 'django.template', 'django.db.backends'}

    def filter(self, record):
        # Проверяем, что логгер в списке разрешённых
        logger_name_allowed = any(record.name.startswith(logger) for logger in self.allowed_loggers)
        # Проверяем уровень
        level_allowed = record.levelno >= logging.ERROR
        return logger_name_allowed and level_allowed


class SecurityLogFilter(logging.Filter):
    """
    Фильтр для security.log: только django.security
    """

    def filter(self, record):
        return record.name.startswith('django.security')