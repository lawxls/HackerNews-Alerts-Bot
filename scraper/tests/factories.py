from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory

from scraper.models import Thread


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
