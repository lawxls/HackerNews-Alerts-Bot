import factory
from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from telegram_feed.models import TelegramUpdate, UserFeed


class TelegramUpdateFactory(DjangoModelFactory):
    update_id = Faker("pyint")
    chat_id = Faker("pyint")
    date = timezone.now()
    text = Faker("text")

    class Meta:
        model = TelegramUpdate


class UserFeedFactory(DjangoModelFactory):
    chat_id = Faker("pyint")
    keywords = ["django", "rust", "sass", "cucumber", "tomato"]
    score_threshold = Faker("pyint", max_value=1000)

    @factory.post_generation
    def threads(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for thread in extracted:
                self.threads.add(thread)

    class Meta:
        model = UserFeed
