import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = {
    "scraper.tasks.comments_scraper_cron_task": {"queue": "scrapers_queue"},
    "scraper.tasks.main_page_threads_scraper_cron_task": {"queue": "scrapers_queue"},
    "scraper.tasks.new_threads_scraper_cron_task": {"queue": "scrapers_queue"},
    "telegram_feed.tasks.send_alerts_task": {"queue": "send_messages_queue"},
    "telegram_feed.tasks.respond_to_messages_task": {"queue": "respond_to_updates_queue"},
}

app.conf.beat_schedule = {
    "new_threads_scraper_cron_task": {
        "task": "scraper.tasks.new_threads_scraper_cron_task",
        "schedule": crontab(minute="*/2"),
    },
    "main_page_threads_scraper_cron_task": {
        "task": "scraper.tasks.main_page_threads_scraper_cron_task",
        "schedule": crontab(minute="*/5"),
    },
    "comments_scraper_cron_task": {
        "task": "scraper.tasks.comments_scraper_cron_task",
        "schedule": crontab(minute="*/1"),
    },
    "respond_to_messages_task": {
        "task": "telegram_feed.tasks.respond_to_messages_task",
        "schedule": 5.0,
    },
    "send_alerts_task": {
        "task": "telegram_feed.tasks.send_alerts_task",
        "schedule": 30,
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
