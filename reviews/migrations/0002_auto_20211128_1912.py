# Generated by Django 3.2.4 on 2021-11-28 16:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favourite',
            unique_together={('content_type', 'object_id', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='star',
            unique_together={('content_type', 'object_id', 'user')},
        ),
    ]
