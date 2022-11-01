from random import choice
from string import ascii_lowercase, digits

import pytest

from telegram_feed.models import UserFeed
from telegram_feed.service import TelegramService
from telegram_feed.tests.factories import TelegramUpdateFactory, UserFeedFactory


class TestTelegramService:
    @pytest.mark.django_db
    def test_respond_to_user_message_start_command_success(self):
        telegram_update = TelegramUpdateFactory.create(text="/start")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == (
            "Hi! To start receiving personalized Hacker News stories you need "
            "to create keywords. Use /add [keyword1, keyword2...] command. "
            "To filter out stories by score "
            "use /set_min_score score command. (Current score threshold is 1). "
            "Type /help for more information"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_help_command_success(self):
        telegram_update = TelegramUpdateFactory.create(text="/help")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "No elp"

    @pytest.mark.django_db
    def test_respond_to_user_message_undefined_command_success(self):
        telegram_update = TelegramUpdateFactory.create()
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "You ok lil bro?"

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_success(self):
        telegram_update = TelegramUpdateFactory.create(
            text="/add python, javascript, rust, linux, booba"
        )
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        keywords_str = "python, javascript, rust, linux, booba"

        assert text_response == (
            "Set up complete! You will be receiving stories "
            f"if story title will contain one of these keywords: {keywords_str}"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_user_feed_exists_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "javascript"])
        telegram_update = TelegramUpdateFactory.create(
            chat_id=1, text="/add cucumber, carrot, tomato, potato, python"
        )
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        user_feed = UserFeed.objects.get(chat_id=1)
        keywords = ["python", "javascript", "cucumber", "carrot", "tomato", "potato"]

        assert set(user_feed.keywords) == set(keywords)
        assert "Keywords added" in text_response

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_many_keywords_error(self):
        chars = ascii_lowercase + digits
        keywords_list = ["".join(choice(chars) for _ in range(5)) for _ in range(101)]
        keywords_str = ", ".join(keywords_list)

        telegram_update = TelegramUpdateFactory.create(text=f"/add {keywords_str}")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == "Too many keywords! Max 100 keywords allowed!"

    @pytest.mark.django_db
    def test_respond_to_user_message_create_keywords_command_lengthy_keyword_error(self):
        keywords_list = ["".join("s" for _ in range(1001)) for _ in range(2)]
        keywords_str = ", ".join(keywords_list)

        telegram_update = TelegramUpdateFactory.create(text=f"/add {keywords_str}")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == (
            "One of the keywords contains too many characters! "
            "Please input keywords that have less than 1000 characters!"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_list_keywords_command_success(self):
        UserFeedFactory.create(
            chat_id=1, keywords=["python", "javascript", "rust", "linux", "booba"]
        )
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/keywords")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        keywords_str = "python, javascript, rust, linux, booba"

        assert text_response == f"Your keywords are: {keywords_str}"

    @pytest.mark.django_db
    def test_respond_to_user_message_list_keywords_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(text="/keywords")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == (
            "To list your keywords you need to create them first. "
            "Use /add [keyword1, keyword2...] command."
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_delete_keywords_command_success(self):
        UserFeedFactory.create(
            chat_id=1, keywords=["python", "javascript", "rust", "linux", "booba"]
        )
        telegram_update = TelegramUpdateFactory.create(
            chat_id=1, text="/remove python, javascript, rust, linux"
        )
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        keywords_str = "booba"

        assert (
            text_response == "Keywords successfully deleted! "
            f"Your current keywords list: {keywords_str}"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_delete_keywords_command_no_more_keywords_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "django"])
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/remove python, django")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        user_feed = UserFeed.objects.filter(chat_id=1).first()

        assert text_response == (
            "Successfully deleted! "
            "You deleted your last keywords and thus you will no longer receive stories!"
        )
        assert user_feed is None

    @pytest.mark.django_db
    def test_respond_to_user_message_delete_keywords_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(
            text="/remove python, javascript, rust, linux"
        )
        text_response = TelegramService(telegram_update=telegram_update).respond_to_user_message()

        assert text_response == (
            "To delete keywords you need to create them first. "
            "Use /add [keyword1, keyword2...] command."
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_set_threshold_command_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "django"])
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/set_threshold 100")
        text_response = TelegramService(
            telegram_update=telegram_update
        ).respond_to_set_threshold_command()

        assert text_response == (
            "Score threshold is set! "
            "From now on you will be receiving stories with 100 score or higher"
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_set_threshold_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(text="/set_threshold 100")
        text_response = TelegramService(
            telegram_update=telegram_update
        ).respond_to_set_threshold_command()

        assert text_response == (
            "To set score threshold create keywords first. "
            "Use /add [keyword1, keyword2...] command."
        )

    @pytest.mark.django_db
    def test_respond_to_user_message_stop_command_success(self):
        UserFeedFactory.create(chat_id=1, keywords=["python", "django"])
        telegram_update = TelegramUpdateFactory.create(chat_id=1, text="/stop")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_stop_command()

        assert text_response == "Success! All your data is gone!"

    @pytest.mark.django_db
    def test_respond_to_user_message_stop_command_not_created_error(self):
        telegram_update = TelegramUpdateFactory.create(text="/stop")
        text_response = TelegramService(telegram_update=telegram_update).respond_to_stop_command()

        assert text_response == "We don't keep any of your data lil bro!"
