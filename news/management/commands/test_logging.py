from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')
server_logger = logging.getLogger('django.server')
template_logger = logging.getLogger('django.template')
db_logger = logging.getLogger('django.db.backends')
security_logger = logging.getLogger('django.security')


class Command(BaseCommand):
    help = 'Тестирование системы логирования'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Тестирование логирования...')

        # Тест DEBUG (должен быть только в консоли при DEBUG=True)
        logger.debug('🐛 DEBUG сообщение')

        # Тест INFO (general.log при DEBUG=False, консоль при DEBUG=True)
        logger.info('ℹ️ INFO сообщение')

        # Тест WARNING (general.log + консоль с pathname)
        logger.warning('⚠️ WARNING сообщение')

        # Тест ERROR (все обработчики)
        try:
            1 / 0
        except Exception as e:
            logger.error('❌ ERROR сообщение', exc_info=True)

        # Тест для django.request
        request_logger.error('🔥 Request error', exc_info=True)

        # Тест для django.server
        server_logger.error('🔧 Server error', exc_info=True)

        # Тест для django.template
        template_logger.error('🎨 Template error', exc_info=True)

        # Тест для django.db.backends
        db_logger.error('💾 DB error', exc_info=True)

        # Тест безопасности
        security_logger.warning('🔐 Security warning: Failed login attempt')
        security_logger.error('🔒 Security error: SQL injection attempt')

        self.stdout.write(self.style.SUCCESS('✅ Тестирование завершено!'))