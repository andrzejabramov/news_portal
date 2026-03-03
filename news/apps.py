# news/apps.py

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """
        Импортируем сигналы при загрузке приложения.
        """
        try:
            import news.signals
            logger.info("✅ news.signals successfully imported")
            print("✅ [NewsConfig] news.signals loaded")  # Для видимости в консоли
        except ImportError as e:
            logger.error(f"❌ Failed to import news.signals: {e}", exc_info=True)
            print(f"❌ [NewsConfig] ImportError: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error in ready(): {e}", exc_info=True)
            print(f"❌ [NewsConfig] Error: {e}")
