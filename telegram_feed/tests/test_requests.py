import pytest

from telegram_feed.requests import GetUpdates


class TestGetUpdates:
    @pytest.mark.django_db
    def test_get_updates_method_success(self):
        update_objs = GetUpdates().get_updates()

        assert isinstance(update_objs, list)
