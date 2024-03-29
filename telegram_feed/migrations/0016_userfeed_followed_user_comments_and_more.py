# Generated by Django 4.1.7 on 2024-02-06 00:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scraper", "0012_thread_creator_username_comment_username_upper_index_and_more"),
        ("telegram_feed", "0015_alter_userfeed_hn_username_followeduser"),
    ]

    operations = [
        migrations.AddField(
            model_name="userfeed",
            name="followed_user_comments",
            field=models.ManyToManyField(related_name="followed_user_feeds", to="scraper.comment"),
        ),
        migrations.AddField(
            model_name="userfeed",
            name="followed_user_threads",
            field=models.ManyToManyField(related_name="followed_user_feeds", to="scraper.thread"),
        ),
    ]
