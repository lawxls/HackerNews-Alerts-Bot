from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class UpdateData:
    """Data from telegram getUpdates method"""

    update_id: int
    chat_id: int
    unix_timestamp_date: int
    text: str


class InlineKeyboardButton(TypedDict):
    text: str
    url: str | None


class UserMessageType:
    START_COMMAND = "START_COMMAND"
    HELP_COMMAND = "HELP_COMMAND"
    LIST_KEYWORDS_COMMAND = "LIST_KEYWORDS_COMMAND"
    CREATE_KEYWORDS_COMMAND = "CREATE_KEYWORDS_COMMAND"
    DELETE_KEYWORDS_COMMAND = "DELETE_KEYWORDS_COMMAND"
    SET_THRESHOLD_COMMAND = "SET_THRESHOLD_COMMAND"
    STOP_COMMAND = "STOP_COMMAND"
    UNDEFINED_COMMAND = "UNDEFINED_COMMAND"
