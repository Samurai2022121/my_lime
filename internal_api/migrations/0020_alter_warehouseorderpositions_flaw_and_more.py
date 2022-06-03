# Generated by Django 4.0.1 on 2022-05-19 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0019_alter_warehouse_max_remaining_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="warehouseorderpositions",
            name="flaw",
            field=models.DecimalField(decimal_places=4, default=0, max_digits=9),
        ),
        migrations.AlterField(
            model_name="warehouseorderpositions",
            name="quantity",
            field=models.DecimalField(decimal_places=4, default=0, max_digits=9),
        ),
        migrations.AlterField(
            model_name="warehouseorderpositions",
            name="special",
            field=models.DecimalField(decimal_places=4, default=0, max_digits=9),
        ),
    ]