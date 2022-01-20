# Generated by Django 3.2.4 on 2022-01-15 17:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0023_alter_warehouseorderpositions_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="warehouseorder",
            name="shop",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="internal_api.shop",
            ),
            preserve_default=False,
        ),
    ]