import re
from time import sleep

from django.db.models.query import QuerySet

from scraper.models import Thread
from telegram_feed.models import UserFeed
from telegram_feed.requests import SendMessage
from telegram_feed.types import InlineKeyboardButton


def send_threads_to_telegram_feed(user_feed: UserFeed, threads: "QuerySet[Thread]") -> bool:
    for thread in threads:
        sleep(1)

        thread_created_at_str = thread.thread_created_at.strftime("%B %d, %H:%M")
        escaped_title = escape_markdown(text=thread.title, version=2)
        escaped_story_link = escape_markdown(text=thread.link, version=2, entity_type="text_link")
        escaped_comments_link = escape_markdown(
            text=thread.comments_link, version=2, entity_type="text_link"  # type: ignore
        )
        text = (
            f"[*{escaped_title}*]({escaped_story_link}) \n\n"
            f"{thread.score}\\+ points \\| [{thread.comments_count}\\+ "
            f"comments]({escaped_comments_link}) \\| {thread_created_at_str}"
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


def escape_markdown(text: str, version: int = 1, entity_type: str = None) -> str:
    """
    Helper function to escape telegram markup symbols.
    Args:
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``1``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.
    """
    if version == 1:
        escape_chars = r"_*`["
    elif version == 2:
        if entity_type in {"pre", "code"}:
            escape_chars = r"\`"
        elif entity_type == "text_link":
            escape_chars = r"\)"
        else:
            escape_chars = r"_*[]()~`>#+-=|{}.!"
    else:
        raise ValueError("Markdown version must be either 1 or 2!")

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
