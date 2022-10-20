from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateData:
    """Data from telegram getUpdates method"""

    update_id: int
    chat_id: int
    unix_timestamp_date: int
    text: str


class UserMessageType:
    START_COMMAND = "START_COMMAND"
    HELP_COMMAND = "HELP_COMMAND"
    LIST_KEYWORDS_COMMAND = "LIST_KEYWORDS_COMMAND"
    CREATE_KEYWORDS_COMMAND = "CREATE_KEYWORDS_COMMAND"
    DELETE_KEYWORDS_COMMAND = "DELETE_KEYWORDS_COMMAND"
    UNDEFINED_COMMAND = "UNDEFINED_COMMAND"