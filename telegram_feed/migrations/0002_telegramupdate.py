# Generated by Django 4.1 on 2022-09-03 21:32

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("telegram_feed", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelegramUpdate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("update_id", models.PositiveIntegerField()),
                ("chat_id", models.PositiveBigIntegerField(verbose_name="telegram chat id")),
                ("date", models.DateTimeField()),
                ("text", models.TextField()),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
    ]
