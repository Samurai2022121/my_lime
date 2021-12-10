# Generated by Django 3.2.4 on 2021-11-21 22:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("orders", "0002_auto_20211122_0106"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Покупатель",
            ),
        ),
    ]