# Generated by Django 4.0.1 on 2022-04-18 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0017_fill_batches"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="warehouse",
            name="supplier",
        ),
    ]