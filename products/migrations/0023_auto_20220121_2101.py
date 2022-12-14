# Generated by Django 3.2.4 on 2022-01-21 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0022_category_is_archive"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="barcode",
            field=models.BigIntegerField(
                blank=True, null=True, verbose_name="Штрихкод"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="in_stock",
            field=models.BooleanField(default=False, verbose_name="Наличие"),
        ),
    ]
