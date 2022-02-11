# Generated by Django 4.0.1 on 2022-02-07 13:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0008_remove_news_image_remove_news_text_newsparagraphs"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="newsparagraphs",
            name="image",
        ),
        migrations.CreateModel(
            name="NewsParagraphsImages",
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
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="news/",
                        verbose_name="Изображение",
                    ),
                ),
                (
                    "news_paragraphs",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="news_paragraphs_images",
                        to="news.newsparagraphs",
                    ),
                ),
            ],
        ),
    ]
