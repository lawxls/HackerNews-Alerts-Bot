# Generated by Django 4.1 on 2022-12-13 19:15

from django.db import migrations


def migrate_keywords(apps, schema_editor):
    UserFeed = apps.get_model("telegram_feed", "UserFeed")
    Keyword = apps.get_model("telegram_feed", "Keyword")

    for user_feed in UserFeed.objects.all():
        for keyword in user_feed.old_keywords:
            Keyword.objects.create(user_feed=user_feed, name=keyword, search_comments=False)


class Migration(migrations.Migration):

    dependencies = [
        ("telegram_feed", "0007_alter_userfeed_old_keywords"),
    ]

    operations = [
        migrations.RunPython(migrate_keywords, migrations.RunPython.noop),
    ]
