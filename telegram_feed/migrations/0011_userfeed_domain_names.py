# Generated by Django 4.1.4 on 2023-03-04 13:19

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("telegram_feed", "0010_rename_subscriptions_userfeed_subscription_threads_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userfeed",
            name="domain_names",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=253), default=list, size=None, verbose_name="domain names"
            ),
        ),
    ]
