# Generated by Django 3.2.4 on 2021-12-14 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0018_auto_20211208_1630"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="measure_unit",
            field=models.CharField(blank=True, max_length=35, null=True),
        ),
    ]