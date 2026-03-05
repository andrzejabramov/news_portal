# news/management/commands/runapscheduler.py

import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Импорт наших задач
from news.utils.email import send_weekly_digest

logger = logging.getLogger(__name__)


def delete_old_job_executions(max_age=604_800):
    """Удаляет старые записи выполнений задач (старше 7 дней)"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
    logger.info("Deleted old job executions")


class Command(BaseCommand):
    help = "Runs apscheduler for periodic tasks."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # =====================================================================
        # ЗАДАЧА 1: Еженедельный дайджест
        # Запуск: каждый понедельник в 09:00
        # =====================================================================
        scheduler.add_job(
            send_weekly_digest,
            # trigger=CronTrigger(day_of_week="mon", hour="9", minute="0"),
            trigger=IntervalTrigger(minutes=1),  # ← Каждую минуту!
            id="weekly_digest_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✅ Added job: 'weekly_digest_job' (Mondays at 09:00)")

        # =====================================================================
        # ЗАДАЧА 2: Очистка старых записей выполнений
        # Запуск: каждое воскресенье в 23:00
        # =====================================================================
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="sun", hour="23", minute="0"),
            id="delete_old_executions_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✅ Added job: 'delete_old_executions_job' (Sundays at 23:00)")

        # =====================================================================
        # ЗАПУСК ПЛАНИРОВЩИКА
        # =====================================================================
        try:
            logger.info("🚀 Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("🛑 Stopping scheduler...")
            scheduler.shutdown()
            logger.info("✅ Scheduler shut down successfully!")
