from telegram_feed.models import TelegramUpdate, UserMessageType


class TelegramService:
    def respond_to_user_message(self, telegram_update: TelegramUpdate) -> str:
        user_message_type = self.check_user_message(telegram_update=telegram_update)

        if user_message_type == UserMessageType.START_COMMAND:
            return self.respond_to_start_command(telegram_update=telegram_update)
        elif user_message_type == UserMessageType.HELP_COMMAND:
            return self.respond_to_help_command(telegram_update=telegram_update)
        elif user_message_type == UserMessageType.LIST_KEYWORDS_COMMAND:
            return self.respond_to_list_keywords_command(telegram_update=telegram_update)
        elif user_message_type == UserMessageType.CREATE_KEYWORDS_COMMAND:
            return self.respond_to_create_keywords_command(telegram_update=telegram_update)
        elif user_message_type == UserMessageType.DELETE_KEYWORDS_COMMAND:
            return self.respond_to_delete_keywords_command(telegram_update=telegram_update)
        else:
            return self.respond_to_undefined_command(telegram_update=telegram_update)

    def check_user_message(self, telegram_update: TelegramUpdate) -> UserMessageType:
        pass

    def respond_to_start_command(self, telegram_update: TelegramUpdate) -> str:
        pass

    def respond_to_help_command(self, telegram_update: TelegramUpdate) -> str:
        pass

    def respond_to_list_keywords_command(self, telegram_update: TelegramUpdate) -> str:
        pass

    def respond_to_create_keywords_command(self, telegram_update: TelegramUpdate) -> str:
        pass

    def respond_to_delete_keywords_command(self, telegram_update: TelegramUpdate) -> str:
        pass

    def respond_to_undefined_command(self, telegram_update: TelegramUpdate) -> str:
        pass
