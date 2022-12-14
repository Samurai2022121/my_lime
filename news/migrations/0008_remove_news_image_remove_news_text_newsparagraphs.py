# Generated by Django 4.0.1 on 2022-02-07 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0007_news_is_archive"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="news",
            name="image",
        ),
        migrations.RemoveField(
            model_name="news",
            name="text",
        ),
        migrations.CreateModel(
            name="NewsParagraphs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subheadline", models.CharField(max_length=255, null=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="news/",
                        verbose_name="Изображение",
                    ),
                ),
                ("text", models.TextField(verbose_name="Текст")),
                (
                    "news",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="news_paragraphs",
                        to="news.news",
                    ),
                ),
            ],
        ),
    ]
