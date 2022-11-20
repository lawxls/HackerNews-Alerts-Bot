import datetime
from unittest import mock

import pytest
from django.utils import timezone

from scraper.tests.factories import ThreadFactory
from telegram_feed.tasks import send_stories_to_user_chats_task
from telegram_feed.tests.factories import UserFeedFactory


class TestSendStoriesToUserChatsTask:
    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_send_stories(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed = UserFeedFactory.create(keywords=["python", "django", "tomato"])

        thread1 = ThreadFactory.create(title="test title with Python keyword")
        thread2 = ThreadFactory.create(title="test title with Django keyword")
        thread3 = ThreadFactory.create(title="test title with tomato keyword")
        thread4 = ThreadFactory.create(title="test title with Cucumber non-existing keyword")

        send_stories_to_user_chats_task()

        assert thread1 in user_feed.threads.all()
        assert thread2 in user_feed.threads.all()
        assert thread3 in user_feed.threads.all()
        assert thread4 not in user_feed.threads.all()

    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_score_threshold(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed = UserFeedFactory.create(keywords=["python", "tomato"], score_threshold=100)

        thread1 = ThreadFactory.create(title="test title with Python keyword", score=500)
        thread2 = ThreadFactory.create(
            title="test title with Python keyword below threshold", score=5
        )
        thread3 = ThreadFactory.create(title="test title with tomato keyword", score=1000)

        send_stories_to_user_chats_task()

        assert thread1 in user_feed.threads.all()
        assert thread3 in user_feed.threads.all()
        assert thread2 not in user_feed.threads.all()

    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_sending_stories_from_past_24_hours(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed = UserFeedFactory.create(
            keywords=["python"],
        )

        date_from = timezone.now() - datetime.timedelta(days=2)
        thread1 = ThreadFactory.create(
            title="test title with Python keyword 2 days old", created=date_from
        )
        thread2 = ThreadFactory.create(
            title="test title with Python keyword new", created=timezone.now()
        )

        send_stories_to_user_chats_task()

        assert thread1 not in user_feed.threads.all()
        assert thread2 in user_feed.threads.all()

    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_sending_stories_to_multiple_user_feeds(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed1 = UserFeedFactory.create(
            keywords=["python", "django"],
        )
        user_feed2 = UserFeedFactory.create(
            keywords=["python", "c++"],
        )

        thread1 = ThreadFactory.create(title="test title with Python keyword")
        thread2 = ThreadFactory.create(title="test title with c++ keyword")
        thread3 = ThreadFactory.create(title="test title with django keyword")

        send_stories_to_user_chats_task()

        assert thread1 in user_feed1.threads.all()
        assert thread3 in user_feed1.threads.all()
        assert thread2 not in user_feed1.threads.all()

        assert thread1 in user_feed2.threads.all()
        assert thread2 in user_feed2.threads.all()
        assert thread3 not in user_feed2.threads.all()
