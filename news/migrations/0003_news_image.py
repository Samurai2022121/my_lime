# Generated by Django 3.2.4 on 2021-11-06 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_alter_news_section"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="news/", verbose_name="Изображение"
            ),
        ),
    ]
