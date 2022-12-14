from config import celery_app
from telegram_feed.models import UserFeed
from telegram_feed.requests import GetUpdatesRequest, SendMessageRequest
from telegram_feed.services import RespondToMessageService, SendAlertsService


@celery_app.task
def send_alerts_task() -> bool:
    user_feeds = UserFeed.objects.all()
    messages_sent_to_feeds = []
    for user_feed in user_feeds:
        send_alerts = SendAlertsService(user_feed=user_feed)

        new_threads = send_alerts.find_new_threads_by_keywords()
        stories_sent = send_alerts.send_threads_to_telegram_feed(threads=new_threads)
        messages_sent_to_feeds.append(stories_sent)
        user_feed.threads.add(*new_threads)

        new_comments, new_comments_by_keywords_dict = send_alerts.find_new_comments_by_keywords()
        comments_sent = send_alerts.send_comments_to_telegram_feed(
            comments_by_keywords=new_comments_by_keywords_dict
        )
        messages_sent_to_feeds.append(comments_sent)
        user_feed.comments.add(*new_comments)

    return all(messages_sent_to_feeds)


@celery_app.task
def respond_to_messages_task() -> bool:

    telegram_updates = GetUpdatesRequest().get_updates()

    send_message_request = SendMessageRequest()
    for update in telegram_updates:
        text_response = RespondToMessageService(telegram_update=update).respond_to_user_message()

        # use MarkdownV2 only for /help and /start commands
        parse_mode: str | None = None
        disable_web_page_preview = False
        if update.text in ["/help", "/start"]:
            parse_mode = "MarkdownV2"
            disable_web_page_preview = True

        send_message_request.send_message(
            chat_id=update.chat_id,
            text=text_response,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )

    return True
