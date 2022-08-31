from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from model_utils.models import TimeStampedModel


class Newsletter(TimeStampedModel, models.Model):
    """Customizable email newsletter"""

    class NewsletterWeekdayChoices(models.TextChoices):
        """Send newsletter on selected day of the week"""

        MONDAY = "MONDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"
        THURSDAY = "THURSDAY"
        FRIDAY = "FRIDAY"
        SATURDAY = "SATURDAY"
        SUNDAY = "SUNDAY"

    name = models.CharField(max_length=200, verbose_name="newsletter name")
    weekday = models.CharField(
        max_length=50,
        choices=NewsletterWeekdayChoices.choices,
        default=NewsletterWeekdayChoices.THURSDAY,
        verbose_name="send newsletter on set weekday",
    )
    email = models.EmailField(verbose_name="subscribed email")
    slug = models.SlugField(max_length=250)
    keywords = ArrayField(models.CharField(max_length=80), verbose_name="newsletter keywords")
    domains = ArrayField(models.CharField(max_length=80), verbose_name="newsletter domains")
    score_threshold = models.PositiveSmallIntegerField(
        verbose_name="filter out stories below set score threshold",
        default=10,
        validators=[MaxValueValidator(1000)],
    )
    stories_per_keyword_max_count = models.PositiveSmallIntegerField(
        verbose_name="max number of stories per keyword",
        validators=[MaxValueValidator(10), MinValueValidator(3)],
    )
    verified = models.BooleanField(default=False, verbose_name="is email verified")

    def __str__(self):
        return f"({self.pk}) {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created"]
