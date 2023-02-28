import json
from collections.abc import Mapping, MutableMapping
from datetime import datetime

import requests
from django.conf import settings
from django.utils.timezone import make_aware

from scraper.utils import start_request_session
from telegram_feed.exceptions import TelegramRequestError
from telegram_feed.models import TelegramUpdate
from telegram_feed.types import InlineKeyboardButton, UpdateData


class GetUpdatesRequest:
    """getUpdates telegram method"""

    def __init__(self, token: str = settings.TELEGRAM_TOKEN) -> None:
        self.token = token

    def get_updates(self) -> list[TelegramUpdate]:
        updates = self.request_updates()
        return self.save_updates(updates=updates)

    def request_updates(self) -> list[UpdateData]:
        """
        Requests telegram updates (user messages)

        raises:
            TelegramRequestError: Telegram API request error
        """

        payload = {"timeout": 2}
        if last_telegram_update := TelegramUpdate.objects.first():
            payload["offset"] = last_telegram_update.update_id + 1

        response = requests.get(f"https://api.telegram.org/bot{self.token}/getUpdates", params=payload)
        json_response = response.json()

        if json_response["ok"] is False:
            if json_response["error_code"] == 409:
                return []
            else:
                # add error_code note in python 3.11
                raise TelegramRequestError("Telegram API request error")

        result = json_response.get("result")

        updates: list[UpdateData] = []
        for update_data_dict in result:
            message = update_data_dict.get("message")
            if not message:
                message = update_data_dict.get("edited_message")

            if message is None:
                continue

            update_data = UpdateData(
                update_id=update_data_dict.get("update_id"),
                chat_id=message.get("chat").get("id"),
                text=message.get("text"),
                unix_timestamp_date=message.get("date"),
            )
            updates.append(update_data)

        return updates

    def save_updates(self, updates: list[UpdateData]) -> list[TelegramUpdate]:
        update_objs: list[TelegramUpdate] = []
        for update_data in updates:
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


class SendMessageRequest:
    """sendMessage telegram method"""

    def __init__(self) -> None:
        self.hn_request_session = start_request_session(
            domen=f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
        )

    def send_message(
        self,
        chat_id: int,
        text: str,
        inline_keyboard_markup: Mapping[str, list[list[InlineKeyboardButton]]] | None = None,
        parse_mode: str | None = None,
        disable_web_page_preview: bool = False,
    ) -> bool:
        payload: MutableMapping[str, int | str] = {"chat_id": chat_id, "text": text}
        if inline_keyboard_markup:
            payload["reply_markup"] = json.dumps(inline_keyboard_markup)
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if disable_web_page_preview:
            payload["disable_web_page_preview"] = disable_web_page_preview

        response = self.hn_request_session.get(
            f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage", params=payload
        )

        return response.json().get("ok") is True
