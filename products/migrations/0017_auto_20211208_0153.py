# Generated by Django 3.2.4 on 2021-12-07 22:53

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0016_product_is_archive"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="is_sorted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="updated_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
    ]