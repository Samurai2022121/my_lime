# Generated by Django 4.0.1 on 2022-03-11 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0029_productunitconversion"),
    ]

    operations = [
        migrations.AddField(
            model_name="productunit",
            name="barcode",
            field=models.BigIntegerField(
                blank=True, null=True, verbose_name="штрихкод"
            ),
        ),
        migrations.AddField(
            model_name="productunit",
            name="for_scales",
            field=models.BooleanField(default=False, verbose_name="весовой товар"),
        ),
        migrations.AddField(
            model_name="productunit",
            name="weight",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=7,
                null=True,
                verbose_name="вес с упаковкой, г",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="product",
            unique_together={("manufacturer", "name")},
        ),
        migrations.RemoveField(
            model_name="product",
            name="barcode",
        ),
        migrations.RemoveField(
            model_name="product",
            name="for_scales",
        ),
        migrations.RemoveField(
            model_name="product",
            name="in_stock",
        ),
        migrations.RemoveField(
            model_name="product",
            name="weight",
        ),
    ]
