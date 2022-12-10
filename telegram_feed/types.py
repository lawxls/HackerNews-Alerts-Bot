from dataclasses import dataclass
from typing import TypedDict

from telegram_feed.models import UserFeed


@dataclass(frozen=True)
class UpdateData:
    """Data from telegram getUpdates method"""

    update_id: int
    chat_id: int
    unix_timestamp_date: int
    text: str


@dataclass
class KeywordData:
    """Keyword data to create Keyword object from"""

    user_feed: UserFeed
    name: str
    is_full_match: bool = False
    search_threads: bool = True
    search_comments: bool = True


class InlineKeyboardButton(TypedDict):
    text: str
    url: str | None
