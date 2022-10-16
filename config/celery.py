import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "thread_scraper_cron_task": {
        "task": "scraper.tasks.thread_scraper_cron_task",
        "schedule": crontab(minute="*/2"),
    },
    "respond_to_updates_task": {
        "task": "telegram_feed.tasks.respond_to_updates_task",
        "schedule": 3.0,
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
