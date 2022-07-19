# Generated by Django 4.0.6 on 2022-07-19 12:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0012_section_permission'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='News',
            new_name='Article',
        ),
        migrations.RenameModel(
            old_name='NewsParagraphs',
            new_name='ArticleParagraph',
        ),
        migrations.RenameModel(
            old_name='NewsParagraphsImages',
            new_name='ArticleParagraphImage',
        ),
    ]
