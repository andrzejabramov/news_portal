import logging


class LevelBasedConsoleHandler(logging.StreamHandler):
    """
    Кастомный обработчик для консоли, который использует разные форматы
    в зависимости от уровня логирования.
    """

    def __init__(self):
        super().__init__()
        # Создаём разные форматеры
        self.formatters = {
            logging.DEBUG: logging.Formatter(
                '{asctime} | {levelname} | {message}',
                style='{',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.INFO: logging.Formatter(
                '{asctime} | {levelname} | {message}',
                style='{',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.WARNING: logging.Formatter(
                '{asctime} | {levelname} | {pathname} | {message}',
                style='{',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.ERROR: logging.Formatter(
                '{asctime} | {levelname} | {pathname} | {message}\n{exc_info}',
                style='{',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
            logging.CRITICAL: logging.Formatter(
                '{asctime} | {levelname} | {pathname} | {message}\n{exc_info}',
                style='{',
                datefmt='%Y-%m-%d %H:%M:%S'
            ),
        }

    def format(self, record):
        # Выбираем форматтер по уровню
        formatter = self.formatters.get(record.levelno, self.formatters[logging.INFO])
        return formatter.format(record)