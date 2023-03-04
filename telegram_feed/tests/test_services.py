from unittest import mock

import pytest

from scraper.tests.factories import CommentFactory, ThreadFactory
from telegram_feed.models import Keyword, UserFeed
from telegram_feed.services import (
    RespondToMessageService,
    SendAlertsService,
    get_keywords_str,
)
from telegram_feed.tests.factories import (
    KeywordFactory,
    TelegramUpdateFactory,
    UserFeedFactory,
)


class TestRespondToMessageService:
    HELP_COMMAND_RESPONSE = (
        "This is [HackerNews](https://news.ycombinator.com/) Alerts Bot 🤖\n\n"
        "Repository: https://github\\.com/lawxls/HackerNews\\-Alerts\\-Bot\n\n"
        "🔻 *FEATURES*:\n\n"
        "● *Keyword alerts*\n\n"
        "Create personal feed of stories or monitor mentions "
        "of your brand, projects or topics you're interested in\\.\n\n"
        "To set up monitoring of story titles and comment bodies, "
        "simply add keyword via `/add` command: `/add python`\n\n"
        "To monitor story titles only, use `-stories` option: `/add python \\-stories`\n\n"
        "In addition, the `/set_score` command can be used to receive stories only if they meet "
        "a specified score threshold \\(set to 1 by default\\)\\.\n\n"
        "Keyword search implemented via case\\-insensitive containment test\\.\n\n\n"
        "● *Subscribe to a thread*\n\n"
        "Monitor new comments of a thread\\.\n\n"
        "Subscribe to a thread by id: `/subscribe 34971530`\n\n\n"
        "🔻 *COMMANDS*\n\n"
        "*Keyword alerts commands*\n\n"
        "● *Add keyword*\n\n"
        "   `/add KEYWORD [\\-whole\\-word, \\-stories, \\-comments]`\n\n"
        "   If no options are specified, the bot will monitor both story titles and comment bodies\\.\n\n"
        "   Options:\n"
        "       ○ `\\-whole\\-word`\n"
        "         match whole word\n\n"
        "       ○ `\\-stories`\n"
        "         only monitor thread titles\n\n"
        "       ○ `\\-comments`\n"
        "         only monitor comment bodies\n\n"
        "   Examples:\n"
        "       ○ `/add project\\-name`\n"
        "       ○ `/add python \\-stories`\n"
        "       ○ `/add AI \\-whole\\-word \\-stories`\n"
        "       ○ `/add machine learning \\-stories`\n\n\n"
        "● *Set score threshold*\n\n"
        "   `/set\\_score SCORE`\n\n"
        "   Receive stories only if they meet a specified score threshold \\(set to 1 by default\\)\\.\n\n\n"
        "● *List keywords*\n\n"
        "   `/keywords`\n\n\n"
        "● *Remove keyword*\n\n"
        "   `/remove KEYWORD`\n\n\n"
        "*Subscribe to a thread commands*\n\n"
        "● *Subscribe to a thread*\n\n"
        "   `/subscribe ID`\n\n\n"
        "● *List subscriptions*\n\n"
        "   `/subscriptions`\n\n\n"
        "● *Unsubscribe from a thread*\n\n"
        "   `/unsubscribe ID`\n\n\n"
        "*General commands*\n\n"
        "● *Commands and other info*\n\n"
        "   `/help`\n\n\n"
        "● *Stop the bot and delete your data*\n\n"
        "   `/stop`\n\n"
    )

    @pytest.mark.django_db
    def test_response_to_start_command(self):
        telegram_update = TelegramUpdateFactory.create(text="/start")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == self.HELP_COMMAND_RESPONSE

    @pytest.mark.django_db
    def test_response_to_help_command(self):
        telegram_update = TelegramUpdateFactory.create(text="/help")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == self.HELP_COMMAND_RESPONSE

    @pytest.mark.django_db
    def test_response_to_undefined_command(self):
        telegram_update = TelegramUpdateFactory.create()
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Huh? Use /help to see the list of implemented commands"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command(self):
        """Test first keyword creation."""

        telegram_update = TelegramUpdateFactory.create(text="/add cucumber")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == (
            "Success! Keyword added. " "You will receive a message when this keyword is mentioned on Hacker News"
        )

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_if_user_feed_exists(self):
        """Test keyword creation if userFeed and some keywords were created before."""

        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="cucumber")
        KeywordFactory.create(user_feed=user_feed, name="tomato")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add pickle")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        keywords_str = get_keywords_str(user_feed)

        assert "pickle" in user_feed.keywords.values_list("name", flat=True)
        assert text_response == f"Success! Keyword added. Current keywords list:\n\n{keywords_str}"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_with_whole_word_option(self):
        """Test add keyword command call with -whole-word option"""

        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="orange")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add tomato -whole-word")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        user_feed = UserFeed.objects.get(chat_id=1)
        keyword = Keyword.objects.get(user_feed=user_feed, name="tomato")

        keywords_str = get_keywords_str(user_feed)
        assert text_response == f"Success! Keyword added. Current keywords list:\n\n{keywords_str}"
        assert keyword.is_full_match is True

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_with_stories_only_option(self):
        """Test add keyword command call with -stories option"""

        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="avocado")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add pickle -stories")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        user_feed = UserFeed.objects.get(chat_id=1)
        keyword = Keyword.objects.get(user_feed=user_feed, name="pickle")

        keywords_str = get_keywords_str(user_feed)
        assert text_response == f"Success! Keyword added. Current keywords list:\n\n{keywords_str}"
        assert keyword.search_comments is False

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_with_comments_only_option(self):
        """Test add keyword command call with -comments option"""

        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="banana")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add cucumber -comments")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        user_feed = UserFeed.objects.get(chat_id=1)
        keyword = Keyword.objects.get(user_feed=user_feed, name="cucumber")

        keywords_str = get_keywords_str(user_feed)
        assert text_response == f"Success! Keyword added. Current keywords list:\n\n{keywords_str}"
        assert keyword.search_threads is False

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_invalid_option_fail(self):
        """Test add keyword command call with invalid option"""

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add cucumber -option-invalid")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Invalid option: option-invalid"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_option_combination_fail(self):
        """Test add keyword command call which raises BadOptionCombinationError error"""

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add cucumber -stories -comments")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! These options cannot be used together: -stories, -comments"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_keywords_limit_fail(self):
        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create_batch(size=50, user_feed=user_feed)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add mango")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! You have reached the limit of 50 keywords"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_keyword_max_length_fail(self):
        keyword = (
            "veryLongKeywordVeryVeryLongWayTooLongveryLongKeywordVeryVeryLong"
            "WayTooLongveryLongKeywordVeryVeryLongWayTooLongveryLongKeywordVeryVeryLongWayTooLong"
        )
        telegram_update = TelegramUpdateFactory.create(text=f"/add {keyword}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Max keyword length is 100 characters"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_keyword_min_length_fail(self):
        telegram_update = TelegramUpdateFactory.create(text="/add L")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Keyword must be at least 2 characters long"

    @pytest.mark.django_db
    def test_response_to_add_keyword_command_keyword_exists_fail(self):
        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="cucumber")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/add cucumber")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Keyword already exists"

    @pytest.mark.django_db
    def test_response_to_list_keywords_command(self):
        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="cucumber")
        KeywordFactory.create(user_feed=user_feed, name="tomato")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/keywords")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        keywords_str = get_keywords_str(user_feed)
        assert text_response == keywords_str

    @pytest.mark.django_db
    def test_response_to_list_keywords_command_no_keywords_fail(self):
        telegram_update = TelegramUpdateFactory.create(text="/keywords")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Add keyword first. /help for info"

    @pytest.mark.django_db
    def test_response_to_remove_keyword_command(self):
        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="cucumber")
        KeywordFactory.create(user_feed=user_feed, name="tomato")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/remove cucumber")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        keywords_str = get_keywords_str(user_feed)
        assert user_feed.keywords.count() == 1
        assert text_response == f"Success! Keyword removed. Current keywords list:\n\n{keywords_str}"

    @pytest.mark.django_db
    def test_response_to_remove_keyword_command_last_keyword_removed(self):
        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="tomato")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/remove tomato")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert user_feed.keywords.count() == 0
        assert text_response == "Success! Last keyword removed"

    @pytest.mark.django_db
    def test_response_to_remove_keyword_command_no_keywords_fail(self):
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/remove potato")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Add keyword first. /help for info"

    @pytest.mark.django_db
    def test_response_to_remove_keyword_command_keyword_not_found_fail(self):
        user_feed = UserFeedFactory.create(chat_id=1)
        KeywordFactory.create(user_feed=user_feed, name="cucumber")

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/remove peach")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Keyword not found"

    @pytest.mark.django_db
    def test_response_to_set_score_command(self):
        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/set_score 100")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Success! Score threshold set to 100"

    @pytest.mark.django_db
    def test_response_to_stop_command(self):
        UserFeedFactory.create(chat_id=1)
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/stop")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Success! Data is erased"

    @pytest.mark.django_db
    def test_response_to_subscribe_command(self):
        UserFeedFactory.create(chat_id=1)

        ThreadFactory.create(title="subscription thread test", thread_id=12345)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/subscribe 12345")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Success! You are now subscribed to a thread: subscription thread test"

    @pytest.mark.django_db
    def test_response_to_subscribe_command_thread_not_found_fail(self):
        UserFeedFactory.create(chat_id=1)

        ThreadFactory.create(title="subscription thread test", thread_id=12345)
        ThreadFactory.create(title="subscription thread test 2", thread_id=54321)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/subscribe 77777")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Thread with 77777 id not found"

    @pytest.mark.django_db
    def test_response_to_subscribe_command_thread_restriction_limit_fail(self):
        subscribed_thread = ThreadFactory.create(title="subscription thread test", thread_id=12345)
        UserFeedFactory.create(chat_id=1, subscription_threads=[subscribed_thread])

        ThreadFactory.create(title="subscription thread test 2", thread_id=54321)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/subscribe 54321")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! You can only subscribe to one thread at a time"

    @pytest.mark.django_db
    def test_response_to_unsubscribe_command(self):
        subscribed_thread = ThreadFactory.create(title="subscription thread test", thread_id=12345)
        UserFeedFactory.create(chat_id=1, subscription_threads=[subscribed_thread])

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/unsubscribe 12345")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Success! You are unsubscribed from a thread: subscription thread test"

    @pytest.mark.django_db
    def test_response_to_unsubscribe_command_not_subscribed_fail(self):
        subscribed_thread = ThreadFactory.create(title="subscription thread test", thread_id=12345)
        UserFeedFactory.create(chat_id=1, subscription_threads=[subscribed_thread])

        thread = ThreadFactory.create(title="subscription thread test 2", thread_id=666666)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/unsubscribe 666666")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == f"Fail! You are not subscribed to thread with {thread.thread_id} id"

    @pytest.mark.django_db
    def test_response_to_list_subscriptions_command(self):
        thread = ThreadFactory.create(title="subscription thread test", thread_id=12345)
        UserFeedFactory.create(chat_id=1, subscription_threads=[thread])

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/subscriptions")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == f"You are subscribed to a thread: {thread.title}\nThread id: {thread.thread_id}"

    @pytest.mark.django_db
    def test_response_to_list_subscriptions_command_not_subscribed_fail(self):
        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/subscriptions")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "You are currently not subscribed to a thread"

    @pytest.mark.django_db
    def test_response_to_follow_command(self):
        domain_name = "example.com"

        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/follow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == f"Success! You are now following {domain_name}"

    @pytest.mark.django_db
    def test_response_to_follow_command_max_length_fail(self):
        domain_name = "d" * 244

        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/follow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Maximum length of a domain name is 243 characters"

    @pytest.mark.django_db
    def test_response_to_follow_command_min_length_fail(self):
        domain_name = "d" * 2

        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/follow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! Minimum length of a domain name is 3 characters"

    @pytest.mark.django_db
    def test_response_to_follow_command_amount_restriction_fail(self):
        domain_name = "example.io"

        UserFeedFactory.create(
            chat_id=1, domain_names=["example.com", "test.com", "example.ai", "example.xyz", "test.ru"]
        )

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/follow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Fail! You are following maximum amount of domain names (5)"

    @pytest.mark.django_db
    def test_response_to_follow_command_already_following_fail(self):
        domain_name = "example.io"

        UserFeedFactory.create(chat_id=1, domain_names=["example.io"])

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/follow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == f"Fail! You are already following {domain_name}"

    @pytest.mark.django_db
    def test_response_to_unfollow_command(self):
        domain_name = "example.io"

        UserFeedFactory.create(chat_id=1, domain_names=["example.io"])

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/unfollow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == f"Success! Unfollowed {domain_name}"

    @pytest.mark.django_db
    def test_response_to_unfollow_command_not_following_fail(self):
        domain_name = "example.io"

        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text=f"/unfollow {domain_name}")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == f"Fail! You are not following {domain_name}"

    @pytest.mark.django_db
    def test_response_to_domains_command(self):
        user_feed = UserFeedFactory.create(chat_id=1, domain_names=["example.io"])

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/domains")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "\n".join(user_feed.domain_names)

    @pytest.mark.django_db
    def test_response_to_domains_command_not_following_fail(self):
        UserFeedFactory.create(chat_id=1)

        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/domains")
        text_response = RespondToMessageService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "You are not following any domain name"


class TestSendAlertsService:
    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_send_subscription_comments_to_telegram_feed(self, send_message_mock):
        send_message_mock.return_value = True

        thread = ThreadFactory.create(title="subscription thread test", thread_id=12345)
        user_feed = UserFeedFactory.create(chat_id=1, subscription_threads=[thread])

        CommentFactory.create(body="comment 1 test", thread_id_int=12345)
        CommentFactory.create(body="2nd comment test", thread_id_int=12345)

        messages_sent = SendAlertsService(user_feed=user_feed).send_subscription_comments_to_telegram_feed()

        assert messages_sent is True

    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_send_threads_to_telegram_feed(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed = UserFeedFactory.create(chat_id=1)
        threads = ThreadFactory.create_batch(size=50)

        messages_sent = SendAlertsService(user_feed=user_feed).send_threads_to_telegram_feed(threads=threads)

        assert messages_sent is True

    @pytest.mark.django_db
    @mock.patch("telegram_feed.requests.SendMessageRequest.send_message")
    def test_send_comments_to_telegram_feed(self, send_message_mock):
        send_message_mock.return_value = True

        user_feed = UserFeedFactory.create(chat_id=1)
        comments_by_keywords = {
            "tomato": [
                CommentFactory.create(body="body that contains tomato keyword"),
                CommentFactory.create(body="body that contains another tomato keyword"),
            ],
            "potato": [
                CommentFactory.create(body="body that contains potato keyword"),
                CommentFactory.create(body="body that contains another potato keyword"),
            ],
        }

        messages_sent = SendAlertsService(user_feed=user_feed).send_comments_to_telegram_feed(
            comments_by_keywords=comments_by_keywords
        )

        assert messages_sent is True

    @pytest.mark.django_db
    def test_find_new_threads_by_keywords(self):
        ThreadFactory.create(title="new thread with potato keyword")
        ThreadFactory.create(title="new thread with tomato keyword")
        sent_thread = ThreadFactory.create(title="already sent thread with tomato keyword")

        user_feed = UserFeedFactory.create(chat_id=1, threads=[sent_thread])

        KeywordFactory.create(user_feed=user_feed, name="tomato", search_comments=False)
        KeywordFactory.create(user_feed=user_feed, name="potato")

        new_threads = SendAlertsService(user_feed=user_feed).find_new_threads_by_keywords()

        assert len(new_threads) == 2
        assert sent_thread not in new_threads

    @pytest.mark.django_db
    def test_find_new_threads_by_keywords_full_word_match(self):
        ThreadFactory.create(title="new thread with tomato keyword")
        ThreadFactory.create(title="new thread with potato keyword")
        unmatched_thread_1 = ThreadFactory.create(title="this is not a full word match - potatoes")
        unmatched_thread_2 = ThreadFactory.create(title="this is not a full word match - tomatoes")

        user_feed = UserFeedFactory.create(chat_id=1)

        KeywordFactory.create(user_feed=user_feed, name="tomato", search_comments=False, is_full_match=True)
        KeywordFactory.create(user_feed=user_feed, name="potato", is_full_match=True)

        new_threads = SendAlertsService(user_feed=user_feed).find_new_threads_by_keywords()

        assert len(new_threads) == 2
        assert unmatched_thread_1 not in new_threads
        assert unmatched_thread_2 not in new_threads

    @pytest.mark.django_db
    def test_find_new_comments_by_keywords(self):
        CommentFactory.create(body="new comment with tomato keyword")
        CommentFactory.create(body="new comment with potato keyword")
        sent_comment = CommentFactory.create(body="already sent comment with tomato keyword")

        user_feed = UserFeedFactory.create(chat_id=1, comments=[sent_comment])

        KeywordFactory.create(user_feed=user_feed, name="tomato", search_threads=False)
        KeywordFactory.create(user_feed=user_feed, name="potato")

        new_comments, new_comments_by_keywords_dict = SendAlertsService(
            user_feed=user_feed
        ).find_new_comments_by_keywords()

        assert len(new_comments) == 2
        assert sent_comment not in new_comments
        assert len(new_comments_by_keywords_dict["tomato"]) == 1
        assert len(new_comments_by_keywords_dict["potato"]) == 1

    @pytest.mark.django_db
    def test_find_new_comments_by_keywords_full_word_match(self):
        CommentFactory.create(body="new comment with tomato keyword")
        CommentFactory.create(body="new comment with potato keyword")
        unmatched_comment_1 = CommentFactory.create(body="this is not a full word match - tomatoes")
        unmatched_comment_2 = CommentFactory.create(body="this is not a full word match - potatoes")

        user_feed = UserFeedFactory.create(chat_id=1)

        KeywordFactory.create(user_feed=user_feed, name="tomato", search_threads=False, is_full_match=True)
        KeywordFactory.create(user_feed=user_feed, name="potato", is_full_match=True)

        new_comments, new_comments_by_keywords_dict = SendAlertsService(
            user_feed=user_feed
        ).find_new_comments_by_keywords()

        assert len(new_comments) == 2
        assert unmatched_comment_1 not in new_comments
        assert unmatched_comment_2 not in new_comments
        assert len(new_comments_by_keywords_dict["tomato"]) == 1
        assert len(new_comments_by_keywords_dict["potato"]) == 1
