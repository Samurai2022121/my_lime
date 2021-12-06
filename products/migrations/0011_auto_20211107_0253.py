# Generated by Django 3.2.4 on 2021-11-06 23:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0010_auto_20211107_0239"),
    ]

    operations = [
        migrations.RenameField(
            model_name="productimages",
            old_name="product_name",
            new_name="description",
        ),
        migrations.RemoveField(
            model_name="product",
            name="images",
        ),
        migrations.RemoveField(
            model_name="product",
            name="main_image",
        ),
        migrations.AddField(
            model_name="productimages",
            name="main",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="productimages",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="products.product",
                verbose_name="Изображения товара",
            ),
        ),
        migrations.AlterField(
            model_name="productimages",
            name="image_1000",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="products/image_1000/",
                verbose_name="1000x1000",
            ),
        ),
        migrations.AlterField(
            model_name="productimages",
            name="image_150",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="products/image_150/",
                verbose_name="150x150",
            ),
        ),
        migrations.AlterField(
            model_name="productimages",
            name="image_500",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="products/image_500/",
                verbose_name="500x500",
            ),
        ),
    ]
