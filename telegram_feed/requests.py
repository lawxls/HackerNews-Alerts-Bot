from datetime import datetime

import requests
from django.conf import settings
from django.utils.timezone import make_aware

from telegram_feed.models import TelegramUpdate
from telegram_feed.types import UpdateData


class GetUpdates:
    """getUpdates telegram method"""

    def __init__(self, token: str = settings.TELEGRAM_TOKEN) -> None:
        self.token = token

    def get_updates(self) -> list[TelegramUpdate] | None:

        updates_data = self.request_updates()
        if updates_data is None:
            return None

        return self.save_updates(updates_data=updates_data)

    def request_updates(self) -> list[UpdateData] | None:

        payload = {"timeout": 2}
        if last_telegram_update := TelegramUpdate.objects.first():
            payload["offset"] = last_telegram_update.update_id + 1

        response = requests.get(
            f"https://api.telegram.org/bot{self.token}/getUpdates", params=payload
        )

        if response.json().get("ok") is False:
            if error_code := response.json().get("error_code"):
                if error_code == 409:
                    return []

        if response.json().get("ok") is True:
            result = response.json().get("result")

            updates_data = []
            for update_data_dict in result:
                update_data = UpdateData(
                    update_id=update_data_dict.get("update_id"),
                    chat_id=update_data_dict.get("message").get("chat").get("id"),
                    text=update_data_dict.get("message").get("text"),
                    unix_timestamp_date=update_data_dict.get("message").get("date"),
                )
                updates_data.append(update_data)

            return updates_data

        return None

    def save_updates(self, updates_data: list[UpdateData]) -> list[TelegramUpdate]:

        update_objs = []
        for update_data in updates_data:
            date = datetime.utcfromtimestamp(update_data.unix_timestamp_date)
            aware_datetime = make_aware(date)

            update_obj = TelegramUpdate.objects.create(
                update_id=update_data.update_id,
                chat_id=update_data.chat_id,
                text=update_data.text,
                date=aware_datetime,
            )
            update_objs.append(update_obj)

        return update_objs


class SendMessage:
    """sendMessage telegram method"""

    def send_message(self, telegram_update: TelegramUpdate, text: str) -> bool:

        payload: dict = {"chat_id": telegram_update.chat_id, "text": text}

        response = requests.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage", params=payload
        )

        return response.json().get("ok") is True
