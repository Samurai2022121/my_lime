# Generated by Django 3.2.4 on 2021-10-14 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_productimages_product_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productimages",
            name="product_name",
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
    ]
