import datetime
from time import sleep

from django.utils import timezone

from config import celery_app
from scraper.models import Thread
from telegram_feed.models import UserFeed
from telegram_feed.requests import GetUpdates, SendMessage
from telegram_feed.service import TelegramService


@celery_app.task
def send_stories_to_user_chats_task():
    date_from = timezone.now() - datetime.timedelta(days=1)
    threads_from_24_hours = Thread.objects.filter(thread_created_at__gte=date_from)

    user_feeds = UserFeed.objects.all()
    for user_feed in user_feeds:
        threads_by_keywords = Thread.objects.none()

        for keyword in user_feed.keywords:
            threads_by_keyword = threads_from_24_hours.filter(
                title__icontains=keyword, score__gte=user_feed.score_threshold
            )
            threads_by_keywords = threads_by_keywords | threads_by_keyword

        new_threads = threads_by_keywords.difference(user_feed.threads.all())
        for new_thread in new_threads:
            sleep(1)

            text = (
                f"{new_thread.title} "
                f"(Score: {new_thread.score}, created: {str(new_thread.thread_created_at)}"
            )
            SendMessage().send_message(chat_id=user_feed.chat_id, text=text)

            user_feed.threads.add(new_thread)


@celery_app.task
def respond_to_updates_task():
    telegram_updates = GetUpdates().get_updates()
    for update in telegram_updates:
        text_response = TelegramService(telegram_update=update).respond_to_user_message()
        SendMessage().send_message(chat_id=update.chat_id, text=text_response)
