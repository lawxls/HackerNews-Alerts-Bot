# Generated by Django 4.1 on 2022-12-01 00:40

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scraper", "0002_thread_thread_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="thread",
            name="thread_id",
            field=models.PositiveBigIntegerField(help_text="thread id", unique=True),
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
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
                ("comment_id", models.PositiveIntegerField(verbose_name="comment id")),
                ("thread_id_int", models.PositiveIntegerField(verbose_name="thread id")),
                (
                    "comment_created_at",
                    models.DateTimeField(verbose_name="parsed comment date of creation"),
                ),
                (
                    "username",
                    models.CharField(max_length=20, verbose_name="comment's creator username"),
                ),
                ("body", models.TextField(verbose_name="comment's text body")),
                (
                    "thread",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="comments",
                        to="scraper.thread",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
    ]
