from time import sleep

from django.db.models.query import QuerySet

from scraper.models import Thread
from telegram_feed.models import UserFeed
from telegram_feed.requests import SendMessage
from telegram_feed.types import InlineKeyboardButton


def send_threads_to_telegram_feed(user_feed: UserFeed, threads: QuerySet[Thread]) -> bool:
    for thread in threads:
        sleep(1)

        thread_created_at_str = thread.thread_created_at.strftime("%B %d, %H:%M")
        text = (
            f"[*{thread.title}*]({thread.link}) \n\n"
            f"{thread.score}\\+ points \\| [{thread.comments_count}\\+ "
            f"comments]({thread.comments_link}) \\| {thread_created_at_str}"
        )

        read_button = InlineKeyboardButton(text="read", url=thread.link)
        comments_button = InlineKeyboardButton(
            text=f"{thread.comments_count}+ comments", url=thread.comments_link
        )

        inline_keyboard_markup = {"inline_keyboard": [[read_button, comments_button]]}

        SendMessage().send_message(
            chat_id=user_feed.chat_id,
            text=text,
            inline_keyboard_markup=inline_keyboard_markup,
            parse_mode="MarkdownV2",
        )

    return True
