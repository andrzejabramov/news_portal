# news/management/commands/send_test_digest.py

from django.core.management.base import BaseCommand
from news.utils.email import send_weekly_digest


class Command(BaseCommand):
    help = "Отправляет тестовый еженедельный дайджест (для отладки)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=int,
            help='ID пользователя для отправки (опционально, по умолчанию — всем)'
        )

    def handle(self, *args, **options):
        self.stdout.write("📰 Запуск тестового дайджеста...")
        
        try:
            result = send_weekly_digest()
            self.stdout.write(self.style.SUCCESS(
                f"✅ Дайджест завершён: {result}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка: {e}"))
            raise
