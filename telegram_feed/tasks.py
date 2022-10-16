from config import celery_app
from telegram_feed.requests import GetUpdates, SendMessage
from telegram_feed.service import TelegramService


@celery_app.task
def respond_to_updates_task():
    telegram_updates = GetUpdates().get_updates()
    for update in telegram_updates:
        text_response = TelegramService().respond_to_user_message(telegram_update=update)
        SendMessage().send_message(telegram_update=update, text=text_response)
