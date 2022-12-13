import datetime
from collections.abc import Iterable, Mapping
from dataclasses import asdict
from time import sleep

from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone

from scraper.models import Comment, Thread
from telegram_feed.exceptions import BadOptionCombinationError, InvalidOptionError
from telegram_feed.models import Keyword, TelegramUpdate, UserFeed
from telegram_feed.requests import SendMessageRequest
from telegram_feed.types import InlineKeyboardButton, KeywordData
from telegram_feed.utils import escape_markdown


class RespondToMessageService:
    """telegram user text response logic"""

    START_COMMAND = "START_COMMAND"
    HELP_COMMAND = "HELP_COMMAND"
    LIST_KEYWORDS_COMMAND = "LIST_KEYWORDS_COMMAND"
    ADD_KEYWORD_COMMAND = "ADD_KEYWORD_COMMAND"
    REMOVE_KEYWORD_COMMAND = "REMOVE_KEYWORD_COMMAND"
    SET_SCORE_COMMAND = "SET_SCORE_COMMAND"
    STOP_COMMAND = "STOP_COMMAND"
    UNDEFINED_COMMAND = "UNDEFINED_COMMAND"

    def __init__(self, telegram_update: TelegramUpdate) -> None:
        self.telegram_update = telegram_update

        # create UserFeed by chat_id if it doesn't exist and set flag
        user_feed = UserFeed.objects.filter(chat_id=telegram_update.chat_id).first()
        user_feed_created = False
        if user_feed is None:
            user_feed = UserFeed.objects.create(chat_id=telegram_update.chat_id)
            user_feed_created = True

        self.user_feed = user_feed
        self.user_feed_created = user_feed_created

    def respond_to_user_message(self) -> str:
        user_message_type = self.check_user_message()

        match user_message_type:
            case self.START_COMMAND:
                return self.respond_to_start_and_help_command()
            case self.HELP_COMMAND:
                return self.respond_to_start_and_help_command()
            case self.LIST_KEYWORDS_COMMAND:
                return self.respond_to_list_keywords_command()
            case self.ADD_KEYWORD_COMMAND:
                return self.respond_to_add_keyword_command()
            case self.REMOVE_KEYWORD_COMMAND:
                return self.respond_to_remove_keyword_command()
            case self.SET_SCORE_COMMAND:
                return self.respond_to_set_score_command()
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
                return self.ADD_KEYWORD_COMMAND
            case ["/remove", _]:
                return self.REMOVE_KEYWORD_COMMAND
            case ["/set_score", score] if score.isnumeric():  # type: ignore
                return self.SET_SCORE_COMMAND
            case ["/stop"]:
                return self.STOP_COMMAND
            case _:
                return self.UNDEFINED_COMMAND

    def respond_to_start_and_help_command(self) -> str:
        return (
            "This is [Hacker News](https://news.ycombinator.com/) notifications bot 🤖\n\n"
            "Repository: https://github\\.com/lawxls/HackerNews\\-personalized\n\n"
            "Currently it can do:\n\n"
            "✨ *Keyword based notifications* ✨\n"
            "Create personal feed or monitor topics, projects you're interested in\\.\n"
            "Keyword search implemented via case\\-insensitive containment test\\.\n\n"
            "To set\\-up:\n"
            "● Add keywords, can specify options for each one "
            "\\(match whole word, scan only thread titles, etc\\)\n"
            "✔️ Done\\! You will receive a message "
            "whenever one of your keywords is mentioned on Hacker News\n\n\n"
            "🔻 *COMMANDS*\n\n"
            "▪️ Add keyword \\(scans comments & stories if options not provided\\)\n"
            "`/add KEYWORD [\\-whole\\-word, \\-stories, \\-comments]`\n\n"
            "*Options:*\n"
            "`\\-whole\\-word`\n"
            "match whole word only\n\n"
            "`\\-stories`\n"
            "scan only thread titles\n\n"
            "`\\-comments`\n"
            "scan only comment bodies\n\n"
            "*Examples:*\n"
            "`/add your-project-name \\-comments`\n"
            "`/add python \\-stories`\n"
            "`/add AI \\-whole\\-word \\-stories`\n\n\n"
            "▪️ Receive story only when it reaches a certain score \\(set to 1 by default\\)\n"
            "`/set\\_score SCORE`\n\n\n"
            "▪️ Get list of your keywords\n"
            "`/keywords`\n\n\n"
            "▪️ Remove keyword from your list\n"
            "`/remove KEYWORD`\n\n\n"
            "▪️ Display this message\n"
            "`/help`\n\n\n"
            "▪️ Stop the bot\\ \\(completely removes your list and your data from database\\)\n"
            "`/stop`"
        )

    def respond_to_list_keywords_command(self) -> str:
        if self.user_feed.keywords.count() == 0:
            return "Fail! Add keyword first. /help for info"

        return get_keywords_str(self.user_feed)

    def respond_to_add_keyword_command(self) -> str:
        # sourcery skip: class-extract-method

        command_data = self.telegram_update.text.replace("/add", "").strip().split(" -")
        keyword = command_data[0]
        options = command_data[1:]

        if len(keyword) > 100:
            return "Fail! Max keyword length is 100 characters"

        if len(keyword) < 2:
            return "Fail! Keyword must be at least 2 characters long"

        if self.user_feed.keywords.count() == 50:
            return "Fail! You have reached the limit of 50 keywords"

        if keyword in self.user_feed.keywords.values_list("name", flat=True):
            return "Fail! Keyword already exists"

        try:
            keyword_data = validate_and_add_options_data_to_keyword(
                keyword_data=KeywordData(user_feed=self.user_feed, name=keyword), options=options
            )
        except BadOptionCombinationError as e:
            options_str = ", ".join(e)
            return f"Fail! These options cannot be used together: {options_str}"
        except InvalidOptionError as e:
            return f"Fail! Invalid option: {e}"

        Keyword.objects.create(**asdict(keyword_data))

        if self.user_feed.keywords.count() == 1:
            return (
                "Success! Keyword added. "
                "You will receive a message when this keyword is mentioned on Hacker News"
            )

        keywords_str = get_keywords_str(self.user_feed)
        return f"Success! Keyword added. Current keywords list:\n\n{keywords_str}"

    def respond_to_remove_keyword_command(self) -> str:
        keyword = self.telegram_update.text.replace("/remove", "").strip()

        if self.user_feed.keywords.count() == 0:
            return "Fail! Add keyword first. /help for info"

        if keyword not in self.user_feed.keywords.values_list("name", flat=True):
            return "Fail! Keyword not found"

        keyword = Keyword.objects.get(user_feed=self.user_feed, name=keyword)
        keyword.delete()

        if self.user_feed.keywords.count() == 0:
            return "Success! Last keyword removed"

        keywords_str = get_keywords_str(self.user_feed)
        return f"Success! Keyword removed. Current keywords list:\n\n{keywords_str}"

    def respond_to_set_score_command(self) -> str:
        command_data = [w.strip() for w in self.telegram_update.text.split()]
        score = int(command_data[1])

        self.user_feed.score_threshold = score
        self.user_feed.save(update_fields=["score_threshold"])

        return f"Success! Score threshold set to {score}"

    def respond_to_stop_command(self) -> str:
        self.user_feed.delete()
        return "Success! Data is erased"

    def respond_to_undefined_command(self) -> str:
        return "Huh? Use /help to see the list of implemented commands"


class SendAlertsService:
    def __init__(self, user_feed: UserFeed):
        self.user_feed = user_feed

    def send_threads_to_telegram_feed(self, threads: Iterable[Thread]) -> bool:
        send_message_request = SendMessageRequest()

        messages_sent: list[bool] = []
        for thread in threads:
            sleep(0.02)

            thread_created_at_str = thread.thread_created_at.strftime("%B %d, %H:%M")
            escaped_title = escape_markdown(text=thread.title, version=2)
            escaped_story_link = escape_markdown(
                text=thread.link, version=2, entity_type="text_link"
            )
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

            sent = send_message_request.send_message(
                chat_id=self.user_feed.chat_id,
                text=text,
                inline_keyboard_markup=inline_keyboard_markup,
                parse_mode="MarkdownV2",
            )
            messages_sent.append(sent)

        return all(messages_sent)

    def send_comments_to_telegram_feed(
        self, comments_by_keywords: Mapping[str, Iterable[Comment]]
    ) -> bool:
        send_message_request = SendMessageRequest()

        messages_sent: list[bool] = []
        for keyword in comments_by_keywords:
            for comment in comments_by_keywords[keyword]:
                sleep(0.02)

                comment_created_at_str = comment.comment_created_at.strftime("%B %d, %H:%M")

                text = (
                    f"Keyword match: {keyword}\n"
                    f"By {comment.username} on {comment_created_at_str}\n\n"
                    f"{comment.body}"
                )

                reply_button = InlineKeyboardButton(
                    text="reply", url=f"{settings.HACKERNEWS_URL}reply?id={comment.comment_id}"
                )
                context_button = InlineKeyboardButton(
                    text="context",
                    url=(
                        f"{settings.HACKERNEWS_URL}item?id="
                        f"{comment.thread_id_int}#{comment.comment_id}"
                    ),
                )

                inline_keyboard_markup = {"inline_keyboard": [[reply_button, context_button]]}

                sent = send_message_request.send_message(
                    chat_id=self.user_feed.chat_id,
                    text=text,
                    inline_keyboard_markup=inline_keyboard_markup,
                    parse_mode=None,
                )
                messages_sent.append(sent)

        return all(messages_sent)

    def find_new_threads_by_keywords(self) -> QuerySet[Thread]:
        keywords = self.user_feed.keywords.filter(search_threads=True)

        date_from = timezone.now() - datetime.timedelta(days=1)
        threads_from_24_hours = Thread.objects.filter(created__gte=date_from)

        threads_by_keywords = Thread.objects.none()

        for keyword in keywords:

            keyword_name = keyword.name
            if keyword.is_full_match is True:
                keyword_name = f" {keyword_name} "

            threads_by_keyword = threads_from_24_hours.filter(
                title__icontains=keyword_name,
                score__gte=self.user_feed.score_threshold,
                comments_link__isnull=False,  # exclude YC hiring posts
            )
            threads_by_keywords = threads_by_keywords | threads_by_keyword

        return threads_by_keywords.difference(self.user_feed.threads.all())

    def find_new_comments_by_keywords(
        self,
    ) -> tuple[QuerySet[Comment], Mapping[str, QuerySet[Comment]]]:
        keywords = self.user_feed.keywords.filter(search_comments=True)

        date_from = timezone.now() - datetime.timedelta(days=1)
        comments_from_24_hours = Comment.objects.filter(created__gte=date_from)

        comments_by_keywords = Comment.objects.none()
        comments_by_keywords_dict: dict[str, QuerySet[Comment]] = {}

        for keyword in keywords:

            if keyword.is_full_match is False:
                comments_by_keyword = comments_from_24_hours.filter(
                    body__search=keyword.name,
                )
            else:
                comments_by_keyword = comments_from_24_hours.filter(
                    body__icontains=f" {keyword.name} ",
                )

            comments_by_keywords_dict[keyword.name] = comments_by_keyword
            comments_by_keywords = comments_by_keywords | comments_by_keyword

        new_comments = comments_by_keywords.difference(self.user_feed.comments.all())
        for k, v in comments_by_keywords_dict.items():
            comments_by_keywords_dict[k] = v.difference(self.user_feed.comments.all())

        return new_comments, comments_by_keywords_dict


def validate_and_add_options_data_to_keyword(
    keyword_data: KeywordData, options: list[str]
) -> KeywordData:

    if "stories" in options and "comments" in options:
        raise BadOptionCombinationError(options=["-stories", "-comments"])

    for option in options:
        match option:
            case "whole-word":
                keyword_data.is_full_match = True
            case "stories":
                keyword_data.search_comments = False
            case "comments":
                keyword_data.search_threads = False
            case _:
                raise InvalidOptionError(option=option)

    return keyword_data


def get_keywords_str(user_feed: UserFeed) -> str:
    """Get list of keywords and it's options as formatted string"""

    keyword_lines = []
    for keyword in user_feed.keywords.all():

        options = []
        if keyword.search_comments is False:
            options.append("stories")
        if keyword.search_threads is False:
            options.append("comments")
        if keyword.is_full_match is True:
            options.append("whole-word")

        options_str = ", ".join(options)
        keyword_line = f"Keyword: {keyword.name}\n" f"Options: {options_str}\n\n"
        keyword_lines.append(keyword_line)

    return "\n".join(keyword_lines)
