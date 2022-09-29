from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateData:
    """Data from telegram getUpdates method"""

    update_id: int
    chat_id: int
    unix_timestamp_date: int
    text: str
