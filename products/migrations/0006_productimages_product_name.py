# Generated by Django 3.2.4 on 2021-10-14 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0005_product_extra_info"),
    ]

    operations = [
        migrations.AddField(
            model_name="productimages",
            name="product_name",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
