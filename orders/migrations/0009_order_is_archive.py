# Generated by Django 3.2.4 on 2021-12-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0008_order_sum_total"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_archive",
            field=models.BooleanField(default=False),
        ),
    ]
