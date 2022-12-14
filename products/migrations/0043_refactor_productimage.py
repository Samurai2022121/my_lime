# Generated by Django 4.0.5 on 2022-06-27 13:10, then edited by @jock_tanner

from django.core import validators
from django.db import migrations
from sorl.thumbnail.fields import ImageField


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0042_alter_product_carbohydrates_alter_product_fats_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ProductImages",
            new_name="ProductImage",
        ),
        migrations.RenameField(
            model_name="productimage",
            old_name="image_1000",
            new_name="image",
        ),
        migrations.RemoveField(
            model_name="productimage",
            name="image_150",
        ),
        migrations.RemoveField(
            model_name="productimage",
            name="image_500",
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=ImageField(
                blank=True,
                null=True,
                upload_to="products/image_1000/",
                verbose_name="оригинал изображения",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="image",
            field=ImageField(
                blank=True,
                null=True,
                upload_to="products/categories/",
                validators=[validators.FileExtensionValidator(["svg", "png", "jpg"])],
                verbose_name="изображение категории",
            ),
        ),
    ]
