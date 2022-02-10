import logging
from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from model_utils.models import TimeStampedModel

logging.basicConfig(level="DEBUG")


class LastWeekThreads(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(created_at__gte=timezone.now() - timedelta(days=7))


class Thread(TimeStampedModel, models.Model):
    """Parsed thread (story, post) from hackernews"""

    thread_id = models.PositiveBigIntegerField(unique=True, help_text="hackernews thread id")
    link = models.URLField(max_length=700)
    title = models.CharField(max_length=100)
    score = models.IntegerField(null=True)
    comments_count = models.IntegerField(null=True)
    comments_link = models.URLField(max_length=250, null=True)
    vector_search = SearchVectorField(null=True)

    objects = models.Manager()
    lastweek = LastWeekThreads()

    def __str__(self):
        return f"({self.pk}) {self.title}"

    class Meta:
        indexes = (GinIndex(fields=["vector_search"]),)
        ordering = ["-score"]


class NewsletterWeekdayChoices(models.TextChoices):
    """The weekday on which the newsletter will be sent"""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class NewsletterThreadsCountChoices(models.TextChoices):
    """Max number of threads per single tag"""

    THREE = 3
    FIVE = 5
    TEN = 10


class Newsletter(TimeStampedModel, models.Model):
    """Customizable email newsletter"""

    name = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    weekday = models.CharField(
        max_length=50,
        choices=NewsletterWeekdayChoices.choices,
        default=NewsletterWeekdayChoices.THURSDAY,
        help_text="""The weekday on which the newsletter will be sent""",
    )
    min_thread_score = models.PositiveSmallIntegerField()
    max_threads_count = models.PositiveSmallIntegerField(
        choices=NewsletterThreadsCountChoices.choices,
        default=NewsletterThreadsCountChoices.FIVE,
        help_text="Max number of threads per single tag",
    )
    slug = models.SlugField(max_length=250)
    tags = ArrayField(models.CharField(max_length=80))
    domens = ArrayField(models.CharField(max_length=80))

    def __str__(self):
        return f"({self.pk}) {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created"]
