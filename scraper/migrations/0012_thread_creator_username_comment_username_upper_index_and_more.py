# Generated by Django 4.1.7 on 2024-02-06 00:28

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):
    dependencies = [
        ("scraper", "0011_alter_comment_options_alter_thread_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="thread",
            name="creator_username",
            field=models.CharField(max_length=15, null=True, verbose_name="thread creator username"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(django.db.models.functions.text.Upper("username"), name="username_upper_index"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["username"], name="username_gin_index", opclasses=["gin_trgm_ops"]
            ),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("username"), name="gin_trgm_ops"
                ),
                name="username_upper_gin_index",
            ),
        ),
        migrations.AddIndex(
            model_name="thread",
            index=models.Index(django.db.models.functions.text.Upper("creator_username"), name="creator_upper_index"),
        ),
        migrations.AddIndex(
            model_name="thread",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["creator_username"], name="creator_gin_index", opclasses=["gin_trgm_ops"]
            ),
        ),
        migrations.AddIndex(
            model_name="thread",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("creator_username"), name="gin_trgm_ops"
                ),
                name="creator_upper_gin_index",
            ),
        ),
    ]
