import pytest

from telegram_feed.requests import GetUpdatesRequest


class TestGetUpdatesRequest:
    @pytest.mark.django_db
    def test_get_updates_method(self):
        update_objs = GetUpdatesRequest().get_updates()

        assert isinstance(update_objs, list)
