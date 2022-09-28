from datetime import datetime

import requests
from django.conf import settings

from telegram_feed.models import TelegramUpdate


class GetUpdates:
    """getUpdates telegram method"""

    def get_updates(self) -> list[TelegramUpdate] | None:

        updates_data = self.request_updates()
        if updates_data is None:
            return None

        return self.save_updates(updates_data=updates_data)

    def request_updates(self) -> list | None:

        payload = {}
        if last_telegram_update := TelegramUpdate.objects.last():
            payload["offset"] = last_telegram_update.update_id + 1

        response = requests.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/getUpdates", params=payload
        )

        if response.json().get("ok") is True:
            return response.json().get("result")

        return None

    def save_updates(self, updates_data: list) -> list[TelegramUpdate]:

        update_objs_list = []
        for update_data in updates_data:

            unix_timestamp = update_data.get("message").get("date")
            date = datetime.utcfromtimestamp(unix_timestamp).strftime("%Y-%m-%d %H:%M:%S")

            update_obj = TelegramUpdate.objects.create(
                update_id=update_data.get("update_id"),
                chat_id=update_data.get("message").get("chat").get("id"),
                text=update_data.get("message").get("text"),
                date=date,
            )
            update_objs_list.append(update_obj)

        return update_objs_list
