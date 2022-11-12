from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models
from model_utils.models import TimeStampedModel

from scraper.models import Thread


class UserFeed(TimeStampedModel, models.Model):
    """Personalized telegram feed"""

    chat_id = models.PositiveIntegerField(verbose_name="telegram chat id")
    keywords = ArrayField(models.CharField(max_length=80), verbose_name="feed keywords")
    score_threshold = models.PositiveSmallIntegerField(
        verbose_name="Threshold to pass for a story to be sent",
        default=2,
        validators=[MaxValueValidator(10000)],
    )
    threads = models.ManyToManyField(Thread, related_name="user_feeds")

    def __str__(self):
        return f"({self.pk}) {self.chat_id}"

    class Meta:
        ordering = ["-created"]


class TelegramUpdate(TimeStampedModel, models.Model):
    """Update data from getUpdates method"""

    update_id = models.PositiveIntegerField()
    chat_id = models.PositiveBigIntegerField(verbose_name="telegram chat id")
    date = models.DateTimeField()
    text = models.TextField()

    def __str__(self):
        return f"({self.pk}) {self.update_id}"

    class Meta:
        ordering = ["-created"]
