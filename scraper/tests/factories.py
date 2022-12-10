import factory
from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from scraper.models import Comment, Thread


class ThreadFactory(DjangoModelFactory):
    thread_id = Faker("pyint")
    title = Faker("sentence")
    link = Faker("url")
    comments_link = Faker("url")
    score = Faker("pyint")
    comments_count = Faker("pyint")
    thread_created_at = timezone.now()
    created = timezone.now()

    class Meta:
        model = Thread


class CommentFactory(DjangoModelFactory):
    thread = factory.SubFactory(ThreadFactory)
    comment_id = Faker("pyint")
    thread_id_int = Faker("pyint")
    comment_created_at = timezone.now()
    username = Faker("name")
    body = Faker("sentence")

    class Meta:
        model = Comment
