# Generated by Django 4.0.1 on 2022-03-13 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0032_remove_product_price"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="product",
            unique_together=set(),
        ),
    ]
