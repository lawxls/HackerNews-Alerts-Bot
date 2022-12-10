from unittest import mock

import pytest

from scraper.tests.factories import CommentFactory, ThreadFactory
from telegram_feed.tasks import send_alerts_task
from telegram_feed.tests.factories import KeywordFactory, UserFeedFactory


class TestSendStoriesToUserChatsTask:
    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_send_alerts_task(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed = UserFeedFactory.create(chat_id=1)

        KeywordFactory.create(user_feed=user_feed, name="tomato")
        KeywordFactory.create(user_feed=user_feed, name="potato")

        thread_1 = ThreadFactory.create(title="thread with tomato keyword")
        thread_2 = ThreadFactory.create(title="thread with potato keyword")
        comment_1 = CommentFactory.create(body="comment with tomato keyword")
        comment_2 = CommentFactory.create(body="comment with potato keyword")

        send_alerts_task()

        assert thread_1 in user_feed.threads.all()
        assert thread_2 in user_feed.threads.all()
        assert comment_1 in user_feed.comments.all()
        assert comment_2 in user_feed.comments.all()

    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_send_alerts_task_send_to_multiple_user_feeds(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed_1 = UserFeedFactory.create(chat_id=1)
        user_feed_2 = UserFeedFactory.create(chat_id=2)

        KeywordFactory.create(user_feed=user_feed_1, name="tomato")
        KeywordFactory.create(user_feed=user_feed_2, name="tomato")

        thread = ThreadFactory.create(title="thread with tomato keyword")
        comment = CommentFactory.create(body="comment with tomato keyword")

        send_alerts_task()

        assert thread in user_feed_1.threads.all()
        assert comment in user_feed_1.comments.all()

        assert thread in user_feed_2.threads.all()
        assert comment in user_feed_2.comments.all()
