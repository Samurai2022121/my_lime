# Generated by Django 4.0.1 on 2022-04-12 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0014_alter_warehouseorder_order_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="shop",
            name="e_shop_base",
            field=models.BooleanField(
                default=False, verbose_name="площадка интернет-магазина"
            ),
        ),
    ]