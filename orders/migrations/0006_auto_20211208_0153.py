# Generated by Django 3.2.4 on 2021-12-07 22:53

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_alter_order_order_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="date_order_placed",
        ),
        migrations.AddField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="order",
            name="updated_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
    ]
