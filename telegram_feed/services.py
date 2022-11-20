from time import sleep

from django.db.models.query import QuerySet

from scraper.models import Thread
from telegram_feed.models import TelegramUpdate, UserFeed
from telegram_feed.requests import SendMessageRequest
from telegram_feed.types import InlineKeyboardButton
from telegram_feed.utils import escape_markdown


class RespondToMessageService:
    """telegram user text response logic"""

    START_COMMAND = "START_COMMAND"
    HELP_COMMAND = "HELP_COMMAND"
    LIST_KEYWORDS_COMMAND = "LIST_KEYWORDS_COMMAND"
    CREATE_KEYWORDS_COMMAND = "CREATE_KEYWORDS_COMMAND"
    DELETE_KEYWORDS_COMMAND = "DELETE_KEYWORDS_COMMAND"
    SET_THRESHOLD_COMMAND = "SET_THRESHOLD_COMMAND"
    STOP_COMMAND = "STOP_COMMAND"
    UNDEFINED_COMMAND = "UNDEFINED_COMMAND"

    def __init__(self, telegram_update: TelegramUpdate) -> None:
        self.telegram_update = telegram_update

    def respond_to_user_message(self) -> str:
        user_message_type = self.check_user_message()

        match user_message_type:
            case self.START_COMMAND:  # same response as help command
                return self.respond_to_help_command()
            case self.HELP_COMMAND:
                return self.respond_to_help_command()
            case self.LIST_KEYWORDS_COMMAND:
                return self.respond_to_list_keywords_command()
            case self.CREATE_KEYWORDS_COMMAND:
                return self.respond_to_create_keywords_command()
            case self.DELETE_KEYWORDS_COMMAND:
                return self.respond_to_delete_keywords_command()
            case self.SET_THRESHOLD_COMMAND:
                return self.respond_to_set_threshold_command()
            case self.STOP_COMMAND:
                return self.respond_to_stop_command()
            case _:
                return self.respond_to_undefined_command()

    def check_user_message(self) -> str:  # type: ignore[return]

        match self.telegram_update.text.split():
            case ["/start"]:
                return self.START_COMMAND
            case ["/help"]:
                return self.HELP_COMMAND
            case ["/keywords"]:
                return self.LIST_KEYWORDS_COMMAND
            case ["/add", _, *_]:
                return self.CREATE_KEYWORDS_COMMAND
            case ["/remove", _, *_]:
                return self.DELETE_KEYWORDS_COMMAND
            case ["/set_score", score] if score.isnumeric():  # type: ignore
                return self.SET_THRESHOLD_COMMAND
            case ["/stop"]:
                return self.STOP_COMMAND
            case _:
                return self.UNDEFINED_COMMAND

    def respond_to_start_command(self) -> str:
        pass

    def respond_to_help_command(self) -> str:
        return (
            "You can use this bot to create personal feed of stories from Hacker News. "
            "Just add keywords, maybe set score threshold (default is 1) "
            "and the bot will send stories when "
            "any of these keywords are mentioned in the title of Hacker News thread. "
            "Keyword search implemented via case-insensitive containment test.\n\n"
            "🔻 COMMANDS\n\n"
            "▪️ /add python, machine learning, _ai_\n\n"
            "Add keywords. Separate by comma.\n"
            "To only match a whole word add underscore before and after desired keyword. "
            "Underscores will be replaced with whitespace, "
            "so '_ai_' will be equivalent to ' ai '.\n"
            "Btw, this will match even if the keyword "
            "is the first or the last word of the title\n\n\n"
            "▪️ /set_score 100\n\n"
            "Filter out stories by score. Default is 1.\n\n\n"
            "▪️ /keywords\n\n"
            "List your keywords.\n\n\n"
            "▪️ /remove python, machine learning, _ai_\n\n"
            "Remove keywords. Separate by comma.\n\n\n"
            "▪️ /help\n\n"
            "Show this message.\n\n\n"
            "▪️ /stop\n\n"
            "Stop the bot. Erases your data."
        )

    def respond_to_list_keywords_command(self) -> str:
        if user_feed := UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first():
            return "\n".join(user_feed.keywords)

        return "Fail! Add keywords first. /help for info"

    def respond_to_create_keywords_command(self) -> str:
        keywords = (
            self.telegram_update.text.replace("/add", "").strip().replace("_", " ").split(", ")
        )

        if len(keywords) > 50:
            return "Fail! Keywords limit of 50 is reached"

        if len(max(keywords, key=len)) > 80:
            return "Fail! Maximum keyword length is 80 characters"

        if len(min(keywords, key=len)) < 3:
            return "Fail! Keywords must be at least 3 characters long"

        if user_feed := UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first():

            current_keywords = user_feed.keywords
            current_keywords.extend(keywords)
            new_keywords_list = sorted(set(current_keywords))

            if len(new_keywords_list) > 50:
                return "Fail! Keywords limit of 50 is reached"

            user_feed.keywords = new_keywords_list
            user_feed.save(update_fields=["keywords"])

            keywords_str = "\n".join(user_feed.keywords)
            return f"Success! Keyword(s) added. Current keywords list:\n{keywords_str}"

        UserFeed.objects.create(chat_id=self.telegram_update.chat_id, keywords=keywords)

        return "Success! Keyword(s) list created. You may want to use /set_score command now"

    def respond_to_delete_keywords_command(self) -> str:
        user_feed = UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first()
        if user_feed is None:
            return "Fail! Add keywords first. /help for info"

        keywords_to_del = (
            self.telegram_update.text.replace("/remove", "").strip().replace("_", " ").split(", ")
        )
        keywords_to_del_set = set(keywords_to_del)
        keywords_set = set(user_feed.keywords)

        if not bool(set(keywords_set) & set(keywords_to_del_set)):
            return "Fail! Not found in keywords list"

        keywords_set.difference_update(keywords_to_del_set)
        updated_keywords = sorted(keywords_set)

        if not updated_keywords:
            user_feed.delete()
            return (
                "Success! Keyword(s) deleted. "
                "As you have emptied your keywords list, the bot will be silent for now"
            )

        user_feed.keywords = updated_keywords
        user_feed.save(update_fields=["keywords"])

        keywords_str = "\n".join(updated_keywords)
        return f"Success! Keyword(s) deleted. Current keywords list:\n{keywords_str}"

    def respond_to_set_threshold_command(self) -> str:
        user_feed = UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first()
        if user_feed is None:
            return "Fail! Add keywords first. /help for info"

        user_feed.score_threshold = int(
            self.telegram_update.text.replace("/set_score", "").strip()
        )
        user_feed.save(update_fields=["score_threshold"])

        return (
            "Success! Score threshold is set. "
            "From now on you will be receiving stories only when they reach "
            f"{user_feed.score_threshold} points"
        )

    def respond_to_stop_command(self) -> str:
        user_feed = UserFeed.objects.filter(chat_id=self.telegram_update.chat_id).first()
        if user_feed is None:
            return "Fail! Bot cannot be stopped (data not found)"

        user_feed.delete()

        return "Success! Bot is stopped, your data is erased"

    def respond_to_undefined_command(self) -> str:
        return "Huh? Type /help to see the list of implemented commands"


def send_threads_to_telegram_feed(user_feed: UserFeed, threads: QuerySet[Thread]) -> bool:
    messages_sent: list[bool] = []
    for thread in threads:
        sleep(1)

        thread_created_at_str = thread.thread_created_at.strftime("%B %d, %H:%M")
        escaped_title = escape_markdown(text=thread.title, version=2)
        escaped_story_link = escape_markdown(text=thread.link, version=2, entity_type="text_link")
        escaped_comments_link = escape_markdown(
            text=thread.comments_link, version=2, entity_type="text_link"  # type: ignore
        )
        text = (
            f"[*{escaped_title}*]({escaped_story_link}) \n\n"
            f"{thread.score}\\+ points \\| [{thread.comments_count}\\+ "
            f"comments]({escaped_comments_link}) \\| {thread_created_at_str}"
        )

        read_button = InlineKeyboardButton(text="read", url=thread.link)
        comments_button = InlineKeyboardButton(
            text=f"{thread.comments_count}+ comments", url=thread.comments_link
        )

        inline_keyboard_markup = {"inline_keyboard": [[read_button, comments_button]]}

        sent = SendMessageRequest().send_message(
            chat_id=user_feed.chat_id,
            text=text,
            inline_keyboard_markup=inline_keyboard_markup,
            parse_mode="MarkdownV2",
        )
        messages_sent.append(sent)

    return all(messages_sent)
