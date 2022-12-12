from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("scraper", "0004_alter_thread_link"),
    ]

    operations = [
        TrigramExtension(),
    ]
