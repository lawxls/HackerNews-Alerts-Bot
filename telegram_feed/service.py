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
        if not self.telegram_update.text:
            return UserMessageType.UNDEFINED_COMMAND

        match self.telegram_update.text.split()[0]:
            case "/start":
                return UserMessageType.START_COMMAND
            case "/help":
                return UserMessageType.HELP_COMMAND
            case "/keywords":
                return UserMessageType.LIST_KEYWORDS_COMMAND
            case "/create":
                return UserMessageType.CREATE_KEYWORDS_COMMAND
            case "/delete":
                return UserMessageType.DELETE_KEYWORDS_COMMAND
            case _:
                return UserMessageType.UNDEFINED_COMMAND

    def respond_to_start_command(self) -> str:

        return (
            "Hi! To start receiving personalized Hacker News stories you need "
            "to create keywords. Use /create [keyword1, keyword2...] command. "
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
            "Use /create [keyword1, keyword2...] command."
        )

    def respond_to_create_keywords_command(self) -> str:
        if user_feed := UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first():
            keywords_str = ", ".join(user_feed.keywords)
            return (
                "Your keywords list has been created already!\n"
                f"Your keywords are: {keywords_str}\n"
                "Type /help to see information about edit or delete keyword commands"
            )

        keywords = self.telegram_update.text.replace("/create", "").strip().split(", ")
        UserFeed.objects.create(chat_id=self.telegram_update.chat_id, keywords=keywords)

        keywords_str = ", ".join(keywords)
        return (
            "Set up complete! You will be receiving stories "
            f"if story title will contain one of these keywords: {keywords_str}"
        )

    def respond_to_delete_keywords_command(self) -> str:
        if user_feed := UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first():
            keywords_to_del = self.telegram_update.text.replace("/delete", "").strip().split(", ")

            keywords = user_feed.keywords
            for k in keywords_to_del:
                if k in keywords:
                    keywords.remove(k)

            user_feed.keywords = keywords
            user_feed.save()

            keywords_str = ", ".join(keywords)
            return f"Keywords successfully deleted! Your current keywords list: {keywords_str}"

        return (
            "To delete keywords you need to create them first. "
            "Use /create [keyword1, keyword2...] command."
        )

    def respond_to_undefined_command(self) -> str:
        return "You ok lil bro?"
