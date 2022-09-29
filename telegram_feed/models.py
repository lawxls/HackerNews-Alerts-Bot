from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models
from model_utils.models import TimeStampedModel


class UserMessageType(models.TextChoices):
    START_COMMAND = "START_COMMAND"
    HELP_COMMAND = "HELP_COMMAND"
    LIST_KEYWORDS_COMMAND = "LIST_KEYWORDS_COMMAND"
    CREATE_KEYWORDS_COMMAND = "CREATE_KEYWORDS_COMMAND"
    DELETE_KEYWORDS_COMMAND = "DELETE_KEYWORDS_COMMAND"
    UNDEFINED_COMMAND = "UNDEFINED_COMMAND"


class UserFeed(TimeStampedModel, models.Model):
    """Personalized telegram feed"""

    chat_id = models.PositiveIntegerField(verbose_name="telegram chat id")
    keywords = ArrayField(models.CharField(max_length=80), verbose_name="feed keywords")
    score_threshold = models.PositiveSmallIntegerField(
        verbose_name="Threshold to pass for a story to be sent",
        default=10,
        validators=[MaxValueValidator(1000)],
    )

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
