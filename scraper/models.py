from django.db import models
from model_utils.models import TimeStampedModel


class Thread(TimeStampedModel, models.Model):
    """Parsed thread (story) from hackernews"""

    thread_id = models.PositiveBigIntegerField(unique=True, help_text="hackernews thread id")
    link = models.URLField(max_length=700, verbose_name="story link")
    title = models.CharField(max_length=100, verbose_name="thread title")
    score = models.IntegerField(null=True, verbose_name="thread score")
    thread_created_at = models.DateTimeField(verbose_name="parsed thread date of creation")
    comments_count = models.IntegerField(null=True, verbose_name="thread comments count")
    comments_link = models.URLField(
        max_length=250, null=True, verbose_name="link to thread comments"
    )

    def __str__(self):
        return f"({self.pk}) {self.title}"

    class Meta:
        ordering = ["-score"]
