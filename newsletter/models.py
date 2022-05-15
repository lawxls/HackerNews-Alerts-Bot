import logging

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.template.defaultfilters import slugify
from model_utils.models import TimeStampedModel

logging.basicConfig(level="DEBUG")


class Newsletter(TimeStampedModel, models.Model):
    """Customizable email newsletter"""

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

    name = models.CharField(max_length=200, verbose_name="newsletter name")
    email = models.EmailField(verbose_name="email subscribed to this newsletter")
    verified = models.BooleanField(default=False, verbose_name="email verified")
    weekday = models.CharField(
        max_length=50,
        choices=NewsletterWeekdayChoices.choices,
        default=NewsletterWeekdayChoices.THURSDAY,
        help_text="""the weekday on which the newsletter will be sent""",
    )
    min_thread_score = models.PositiveSmallIntegerField()
    max_threads_count = models.PositiveSmallIntegerField(
        choices=NewsletterThreadsCountChoices.choices,
        default=NewsletterThreadsCountChoices.FIVE,
        help_text="max number of threads per single tag",
    )
    slug = models.SlugField(max_length=250)
    tags = ArrayField(models.CharField(max_length=80), verbose_name="newsletter tags")
    domens = ArrayField(models.CharField(max_length=80), verbose_name="newsletter domens")

    def __str__(self):
        return f"({self.pk}) {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created"]
