# Generated by Django 3.2.4 on 2021-12-16 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0010_alter_warehouse_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="warehouse",
            name="shop",
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
