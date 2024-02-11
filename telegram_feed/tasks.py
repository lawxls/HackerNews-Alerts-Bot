from config import celery_app
from telegram_feed.models import UserFeed
from telegram_feed.requests import GetUpdatesRequest, SendMessageRequest
from telegram_feed.services import RespondToMessageService, SendAlertsService


@celery_app.task(time_limit=250)
def send_alerts_task() -> bool:
    user_feeds = UserFeed.objects.prefetch_related(
        "comments",
        "threads",
        "keywords",
        "follow_list",
        "subscription_threads",
        "subscription_comments",
        "reply_comments",
    )
    messages_sent_to_feeds = []
    for user_feed in user_feeds:
        send_alerts = SendAlertsService(user_feed=user_feed)

        # send stories by keywords
        new_threads = send_alerts.find_new_threads_by_keywords()
        stories_sent = send_alerts.send_threads_to_telegram_feed(threads=new_threads)
        messages_sent_to_feeds.append(stories_sent)
        user_feed.threads.add(*new_threads)

        # send comments by keywords
        new_comments, new_comments_by_keywords_dict = send_alerts.find_new_comments_by_keywords()
        comments_sent = send_alerts.send_comments_to_telegram_feed(comments_by_keywords=new_comments_by_keywords_dict)
        messages_sent_to_feeds.append(comments_sent)
        user_feed.comments.add(*new_comments)

        # send comments by subscribed threads
        if user_feed.subscription_threads.exists():
            send_alerts.send_subscription_comments_to_telegram_feed()

        # send stories by domain names
        new_stories = send_alerts.find_new_stories_by_domain_names()
        stories_sent = send_alerts.send_threads_to_telegram_feed(threads=new_stories)
        messages_sent_to_feeds.append(stories_sent)
        user_feed.threads.add(*new_stories)

        # send comments (reply notifications)
        if user_feed.hn_username:
            new_reply_comments = send_alerts.find_new_reply_comments()
            send_alerts.send_reply_comments_to_telegram_feed(comments=new_reply_comments)
            user_feed.reply_comments.add(*new_reply_comments)

        # send stories by followed users
        new_followed_users_threads = send_alerts.find_new_followed_users_threads()
        send_alerts.send_new_followed_users_threads_to_telegram_feed(threads=new_followed_users_threads)
        user_feed.followed_user_threads.add(*new_followed_users_threads)

        # send comments by followed users
        new_followed_users_comments = send_alerts.find_new_followed_users_comments()
        send_alerts.send_new_followed_users_comments_to_telegram_feed(comments=new_followed_users_comments)
        user_feed.followed_user_comments.add(*new_followed_users_comments)

    return all(messages_sent_to_feeds)


@celery_app.task(time_limit=60)
def respond_to_messages_task() -> bool:
    telegram_updates = GetUpdatesRequest().get_updates()

    send_message_request = SendMessageRequest()
    for update in telegram_updates:
        text_response = RespondToMessageService(telegram_update=update).respond_to_user_message()

        parse_mode: str | None = None
        disable_web_page_preview = False
        if update.text in ["/help", "/start", "/commands", "/contacts"]:
            disable_web_page_preview = True

        send_message_request.send_message(
            chat_id=update.chat_id,
            text=text_response,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )

    return True
