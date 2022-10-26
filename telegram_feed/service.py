from telegram_feed.models import TelegramUpdate, UserFeed
from telegram_feed.types import UserMessageType


class TelegramService:
    """telegram user text response logic"""

    def __init__(self, telegram_update: TelegramUpdate) -> None:
        self.telegram_update = telegram_update

    def respond_to_user_message(self) -> str:
        user_message_type = self.check_user_message()

        match user_message_type:
            case UserMessageType.START_COMMAND:
                return self.respond_to_start_command()
            case UserMessageType.HELP_COMMAND:
                return self.respond_to_help_command()
            case UserMessageType.LIST_KEYWORDS_COMMAND:
                return self.respond_to_list_keywords_command()
            case UserMessageType.CREATE_KEYWORDS_COMMAND:
                return self.respond_to_create_keywords_command()
            case UserMessageType.DELETE_KEYWORDS_COMMAND:
                return self.respond_to_delete_keywords_command()
            case _:
                return self.respond_to_undefined_command()

    def check_user_message(self) -> str:

        match self.telegram_update.text.split():
            case ["/start"]:
                return UserMessageType.START_COMMAND
            case ["/help"]:
                return UserMessageType.HELP_COMMAND
            case ["/keywords"]:
                return UserMessageType.LIST_KEYWORDS_COMMAND
            case ["/add", _, *_]:
                return UserMessageType.CREATE_KEYWORDS_COMMAND
            case ["/remove", _, *_]:
                return UserMessageType.DELETE_KEYWORDS_COMMAND
            case _:
                return UserMessageType.UNDEFINED_COMMAND

    def respond_to_start_command(self) -> str:

        return (
            "Hi! To start receiving personalized Hacker News stories you need "
            "to create keywords. Use /add [keyword1, keyword2...] command. "
            "To filter out stories by score "
            "use /set_min_score score command. (Current score threshold is 1). "
            "Type /help for more information"
        )

    def respond_to_help_command(self) -> str:
        return "No elp"

    def respond_to_list_keywords_command(self) -> str:
        if user_feed := UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first():
            keywords_str = ", ".join(user_feed.keywords)
            return f"Your keywords are: {keywords_str}"

        return (
            "To list your keywords you need to create them first. "
            "Use /add [keyword1, keyword2...] command."
        )

    def respond_to_create_keywords_command(self) -> str:
        keywords = self.telegram_update.text.replace("/add", "").strip().split(", ")

        if user_feed := UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first():

            current_keywords = user_feed.keywords
            current_keywords.extend(keywords)
            user_feed.keywords = sorted(set(current_keywords))
            user_feed.save()

            keywords_str = ", ".join(user_feed.keywords)
            return "Keywords added. " f"Your current keywords list: {keywords_str}"

        if len(keywords) > 100:
            return "Too many keywords! Max 100 keywords allowed!"

        if len(max(keywords, key=len)) > 1000:
            return (
                "One of the keywords contains too many characters! "
                "Please input keywords that have less than 1000 characters!"
            )

        UserFeed.objects.create(chat_id=self.telegram_update.chat_id, keywords=keywords)

        keywords_str = ", ".join(keywords)
        return (
            "Set up complete! You will be receiving stories "
            f"if story title will contain one of these keywords: {keywords_str}"
        )

    def respond_to_delete_keywords_command(self) -> str:
        user_feed = UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first()
        if user_feed is None:
            return (
                "To delete keywords you need to create them first. "
                "Use /add [keyword1, keyword2...] command."
            )

        keywords_to_del = self.telegram_update.text.replace("/remove", "").strip().split(", ")
        keywords_to_del_set = set(keywords_to_del)
        keywords_set = set(user_feed.keywords)
        keywords_set.difference_update(keywords_to_del_set)
        updated_keywords = sorted(keywords_set)
        user_feed.keywords = updated_keywords
        user_feed.save()

        if not updated_keywords:
            user_feed.delete()
            return (
                "Successfully deleted! "
                "You deleted your last keywords and thus you will no longer receive stories!"
            )

        keywords_str = ", ".join(updated_keywords)
        return f"Keywords successfully deleted! Your current keywords list: {keywords_str}"

    def respond_to_undefined_command(self) -> str:
        return "You ok lil bro?"
