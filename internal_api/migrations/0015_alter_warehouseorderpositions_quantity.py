# Generated by Django 3.2.4 on 2021-12-19 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0014_remove_warehouseorder_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="warehouseorderpositions",
            name="quantity",
            field=models.FloatField(default=0),
        ),
    ]
