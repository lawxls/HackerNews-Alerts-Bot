from datetime import datetime

import requests
from django.conf import settings
from django.utils.timezone import make_aware

from telegram_feed.models import TelegramUpdate


class GetUpdates:
    """getUpdates telegram method"""

    def get_updates(self, token: str = settings.TELEGRAM_TOKEN) -> list[TelegramUpdate] | None:

        updates_data = self.request_updates(token=token)
        if updates_data is None:
            return None

        return self.save_updates(updates_data=updates_data)

    def request_updates(self, token: str = settings.TELEGRAM_TOKEN) -> list | None:

        payload = {}
        if last_telegram_update := TelegramUpdate.objects.first():
            payload["offset"] = last_telegram_update.update_id + 1

        response = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params=payload)

        if response.json().get("ok") is True:
            return response.json().get("result")

        return None

    def save_updates(self, updates_data: list) -> list[TelegramUpdate]:

        update_objs_list = []
        for update_data in updates_data:
            unix_timestamp = update_data.get("message").get("date")
            date = datetime.utcfromtimestamp(unix_timestamp)
            aware_datetime = make_aware(date)

            update_obj = TelegramUpdate.objects.create(
                update_id=update_data.get("update_id"),
                chat_id=update_data.get("message").get("chat").get("id"),
                text=update_data.get("message").get("text"),
                date=aware_datetime,
            )
            update_objs_list.append(update_obj)

        return update_objs_list


class SendMessage:
    """"""

    def send_message(self, update_obj: TelegramUpdate, text: str) -> bool:
        pass
