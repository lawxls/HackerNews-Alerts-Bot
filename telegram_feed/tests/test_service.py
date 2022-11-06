from random import choice
from string import ascii_lowercase, digits

import pytest

from telegram_feed.models import UserFeed
from telegram_feed.service import RespondToMessageService
from telegram_feed.tests.factories import TelegramUpdateFactory, UserFeedFactory


class TestRespondToMessageService:

    HELP_COMMAND_RESPONSE = (
        "This is a bot for creating your own, personalized feed of stories from Hacker News.\n"
        "Manage your keywords, set score threshold.\n"
        "Keyword search implemented via case-insensitive containment test.\n\n"
        "🔻 COMMANDS\n\n"
        "/add keyword1, second keyword, keyword3\n"
        "Add keywords. Separate by comma.\n\n"
        "/set_score 100\n"
        "Receive stories only when they reach a certain score. Default is 10.\n\n"
        "/keywords\n"
        "List your keywords.\n\n"
        "/remove keyword1, second keyword, keyword3\n"
        "Remove keywords. Separate by comma.\n\n"
        "/help\n"
        "Show this message.\n\n"
        "/stop\n"
        "Stop the bot. Erases your data."
    )

    @pytest.mark.django_db
    def test_respond_to_user_message_start_command_success(self):
        telegram_update = TelegramUpdateFactory.create(text="/start")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == self.HELP_COMMAND_RESPONSE

    @pytest.mark.django_db
    def test_respond_to_user_message_help_command_success(self):
        telegram_update = TelegramUpdateFactory.create(text="/help")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == self.HELP_COMMAND_RESPONSE

    @pytest.mark.django_db
    def test_respond_to_user_message_undefined_command_success(self):
        telegram_update = TelegramUpdateFactory.create()
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == "Huh? Type /help to see the list of implemented commands"

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_success(self):
        telegram_update = TelegramUpdateFactory.create(
            text="/add python, javascript, rust, linux, booba"
        )
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert (
            text_response
            == "Success! Keyword(s) list created. You may want to use /set_score command now"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_user_feed_exists_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "javascript"])
        telegram_update = TelegramUpdateFactory.create(
            chat_id=1, text="/add cucumber, carrot, tomato, potato, python"
        )
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        user_feed = UserFeed.objects.get(chat_id=1)
        keywords = ["python", "javascript", "cucumber", "carrot", "tomato", "potato"]

        assert set(user_feed.keywords) == set(keywords)
        assert "Success! Keyword(s) added. Current keywords list:" in text_response

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_many_keywords_error(self):
        chars = ascii_lowercase + digits
        keywords_list = ["".join(choice(chars) for _ in range(5)) for _ in range(51)]
        keywords_str = ", ".join(keywords_list)

        telegram_update = TelegramUpdateFactory.create(text=f"/add {keywords_str}")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == "Fail! Keywords limit of 50 is reached"

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_lengthy_keyword_error(self):
        keywords_list = ["".join("s" for _ in range(1001)) for _ in range(2)]
        keywords_str = ", ".join(keywords_list)

        telegram_update = TelegramUpdateFactory.create(text=f"/add {keywords_str}")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == "Fail! Maximum keyword length is 80 characters"

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_short_keyword_error(self):
        keywords_list = ["".join("s" for _ in range(2)) for _ in range(2)]
        keywords_str = ", ".join(keywords_list)

        telegram_update = TelegramUpdateFactory.create(text=f"/add {keywords_str}")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == "Fail! Keywords must be at least 3 characters long"

    @pytest.mark.django_db
    def test_respond_to_user_message_list_keywords_command_success(self):
        UserFeedFactory.create(
            chat_id=1, keywords=["python", "javascript", "rust", "linux", "booba"]
        )
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/keywords")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        keywords_str = "python, javascript, rust, linux, booba"

        assert text_response == keywords_str

    @pytest.mark.django_db
    def test_respond_to_user_message_list_keywords_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(text="/keywords")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == "Fail! Add keywords first. /help for info"

    @pytest.mark.django_db
    def test_respond_to_user_message_delete_keywords_command_success(self):
        UserFeedFactory.create(
            chat_id=1, keywords=["python", "javascript", "rust", "linux", "booba"]
        )
        telegram_update = TelegramUpdateFactory.create(
            chat_id=1, text="/remove python, javascript, rust, linux"
        )
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        keywords_str = "booba"

        assert (
            text_response == f"Success! Keyword(s) deleted.\nCurrent keywords list: {keywords_str}"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_delete_keywords_command_no_more_keywords_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "django"])
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/remove python, django")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        user_feed = UserFeed.objects.filter(chat_id=1).first()

        assert text_response == (
            "Success! Keyword(s) deleted. "
            "As you have emptied your keywords list, the bot will be silent for now"
        )
        assert user_feed is None

    @pytest.mark.django_db
    def test_respond_to_user_message_delete_keywords_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(
            text="/remove python, javascript, rust, linux"
        )
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_user_message()

        assert text_response == "Fail! Add keywords first. /help for info"

    @pytest.mark.django_db
    def test_respond_to_user_message_set_threshold_command_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "django"])
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/set_score 100")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_set_threshold_command()

        assert text_response == (
            "Success! Score threshold is set. "
            "From now on you will be receiving stories only when they reach "
            "100 points"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_set_threshold_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(text="/set_score 100")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_set_threshold_command()

        assert text_response == "Fail! Add keywords first. /help for info"

    @pytest.mark.django_db
    def test_respond_to_user_message_stop_command_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "django"])
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/stop")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_stop_command()

        assert text_response == "Success! Bot is stopped, the data is erased"

    @pytest.mark.django_db
    def test_respond_to_user_message_stop_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(text="/stop")
        text_response = RespondToMessageService(
            telegram_update=telegram_update
        ).respond_to_stop_command()

        assert text_response == "Fail! Bot cannot be stopped (data not found)"
