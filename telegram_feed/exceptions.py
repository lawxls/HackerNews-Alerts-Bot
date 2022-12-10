class TelegramRequestError(Exception):
    """Telegram API request error"""


class InvalidOptionError(Exception):
    """Command option doesn't exist error"""

    def __init__(self, option: str) -> None:
        super().__init__(option)


class BadOptionCombinationError(Exception):
    """Command options cannot be used together error"""

    def __init__(self, options: list[str]) -> None:
        self.options = options
        super().__init__(options)

    def __iter__(self):
        yield from self.options
