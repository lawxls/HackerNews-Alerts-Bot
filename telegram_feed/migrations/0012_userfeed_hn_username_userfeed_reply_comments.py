# Generated by Django 4.1.4 on 2023-03-08 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scraper", "0010_comment_parent_comment_alter_comment_comment_id"),
        ("telegram_feed", "0011_userfeed_domain_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="userfeed",
            name="hn_username",
            field=models.CharField(max_length=20, null=True, verbose_name="hacker news username"),
        ),
        migrations.AddField(
            model_name="userfeed",
            name="reply_comments",
            field=models.ManyToManyField(related_name="reply_user_feeds", to="scraper.comment"),
        ),
    ]
