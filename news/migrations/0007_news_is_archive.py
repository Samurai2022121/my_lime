# Generated by Django 3.2.4 on 2021-12-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0006_alter_news_section"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="is_archive",
            field=models.BooleanField(default=False),
        ),
    ]
