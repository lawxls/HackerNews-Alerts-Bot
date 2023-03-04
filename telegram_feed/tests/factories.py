import factory
from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from telegram_feed.models import Keyword, TelegramUpdate, UserFeed


class TelegramUpdateFactory(DjangoModelFactory):
    update_id = factory.Sequence(lambda n: n)
    chat_id = factory.Sequence(lambda n: n)
    date = timezone.now()
    text = Faker("text")

    class Meta:
        model = TelegramUpdate


class UserFeedFactory(DjangoModelFactory):
    chat_id = factory.Sequence(lambda n: n)
    score_threshold = 1
    domain_names: list[str] = []

    @factory.post_generation
    def threads(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for thread in extracted:
                self.threads.add(thread)

    @factory.post_generation
    def subscription_threads(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for thread in extracted:
                self.subscription_threads.add(thread)

    @factory.post_generation
    def comments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for comment in extracted:
                self.comments.add(comment)

    @factory.post_generation
    def subscription_comments(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for comment in extracted:
                self.subscription_comments.add(comment)

    class Meta:
        model = UserFeed


class KeywordFactory(DjangoModelFactory):
    user_feed = factory.SubFactory(UserFeedFactory)
    name = Faker("name")
    is_full_match = False
    search_threads = True
    search_comments = True

    class Meta:
        model = Keyword
