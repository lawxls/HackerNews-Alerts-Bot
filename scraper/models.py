from django.contrib.postgres.indexes import GinIndex, OpClass, HashIndex
from django.db import models
from django.db.models.functions import Upper
from model_utils.models import TimeStampedModel


class Thread(TimeStampedModel, models.Model):
    """Parsed thread (story)"""

    thread_id = models.PositiveBigIntegerField(unique=True, help_text="thread id")
    link = models.URLField(max_length=2000, verbose_name="story link")
    title = models.CharField(max_length=100, verbose_name="thread title", db_index=True)
    creator_username = models.CharField(max_length=15, null=True, verbose_name="thread creator username")
    score = models.IntegerField(null=True, verbose_name="thread score")
    thread_created_at = models.DateTimeField(verbose_name="parsed thread date of creation")
    comments_count = models.IntegerField(null=True, verbose_name="thread comments count")
    comments_link = models.URLField(max_length=250, null=True, verbose_name="link to thread comments")

    def __str__(self):
        return f"({self.pk}) {self.title} by {self.creator_username}"

    class Meta:
        indexes = [
            models.Index(Upper("title"), name="title_upper_index"),
            GinIndex(fields=["title"], name="title_gin_index", opclasses=["gin_trgm_ops"]),
            GinIndex(OpClass(Upper("title"), name="gin_trgm_ops"), name="title_upper_gin_index"),
            models.Index(Upper("creator_username"), name="creator_upper_index"),
            GinIndex(fields=["creator_username"], name="creator_gin_index", opclasses=["gin_trgm_ops"]),
            GinIndex(OpClass(Upper("creator_username"), name="gin_trgm_ops"), name="creator_upper_gin_index"),
        ]


class Comment(TimeStampedModel, models.Model):
    """Parsed thread comment"""

    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True, related_name="comments")
    parent_comment = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="child_comments")
    comment_id = models.PositiveIntegerField(verbose_name="comment id", db_index=True)
    thread_id_int = models.PositiveIntegerField(verbose_name="thread id")
    comment_created_at = models.DateTimeField(verbose_name="parsed comment date of creation")
    username = models.CharField(max_length=20, verbose_name="comment's creator username")
    body = models.CharField(max_length=20000, verbose_name="comment's text body")

    def __str__(self):
        return f"({self.pk}) {self.body[:100]}"

    class Meta:
        indexes = [
            HashIndex(fields=("body",)),
            models.Index(Upper("username"), name="username_upper_index"),
            GinIndex(fields=["username"], name="username_gin_index", opclasses=["gin_trgm_ops"]),
            GinIndex(OpClass(Upper("username"), name="gin_trgm_ops"), name="username_upper_gin_index"),
        ]
