from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models
from model_utils.models import TimeStampedModel

from scraper.models import Comment, Thread


class UserFeed(TimeStampedModel, models.Model):
    """Telegram user feed"""

    chat_id = models.PositiveBigIntegerField(verbose_name="telegram chat id")
    hn_username = models.CharField(max_length=15, null=True, verbose_name="hacker news username")
    old_keywords = ArrayField(models.CharField(max_length=80), default=list, verbose_name="feed keywords")
    domain_names = ArrayField(models.CharField(max_length=253), default=list, verbose_name="domain names")
    score_threshold = models.PositiveSmallIntegerField(
        verbose_name="Threshold to pass for a story to be sent",
        default=1,
        validators=[MaxValueValidator(10000)],
    )
    threads = models.ManyToManyField(Thread, related_name="user_feeds")
    comments = models.ManyToManyField(Comment, related_name="user_feeds")
    subscription_threads = models.ManyToManyField(Thread, related_name="subscription_user_feeds")
    subscription_comments = models.ManyToManyField(Comment, related_name="subscription_user_feeds")
    reply_comments = models.ManyToManyField(Comment, related_name="reply_user_feeds")
    followed_user_threads = models.ManyToManyField(Thread, related_name="followed_user_feeds")
    followed_user_comments = models.ManyToManyField(Comment, related_name="followed_user_feeds")

    def __str__(self):
        return f"({self.pk}) {self.chat_id}"


class TelegramUpdate(TimeStampedModel, models.Model):
    """Update data from getUpdates method"""

    update_id = models.PositiveBigIntegerField()
    chat_id = models.PositiveBigIntegerField(verbose_name="telegram chat id")
    date = models.DateTimeField()
    text = models.TextField()

    def __str__(self):
        return f"({self.pk}) {self.update_id}"


class Keyword(TimeStampedModel, models.Model):
    """Keyword to search for and it's data"""

    user_feed = models.ForeignKey(UserFeed, on_delete=models.CASCADE, related_name="keywords")
    name = models.CharField(max_length=100, validators=[MinLengthValidator(2)], verbose_name="keyword itself")
    is_full_match = models.BooleanField(default=False, verbose_name="search a whole word match")
    search_threads = models.BooleanField(default=True, verbose_name="search in thread's title field")
    search_comments = models.BooleanField(default=True, verbose_name="search in comment's body field")

    def __str__(self):
        return f"({self.pk}) {self.name}"


class FollowedUser(TimeStampedModel, models.Model):
    """Followed Hacker News User"""

    user_feed = models.ForeignKey(UserFeed, on_delete=models.CASCADE, related_name="follow_list")
    username = models.CharField(max_length=15, verbose_name="hacker news username")
    follow_threads = models.BooleanField(default=True, verbose_name="follow user's threads")
    follow_comments = models.BooleanField(default=True, verbose_name="follow user's comments")
