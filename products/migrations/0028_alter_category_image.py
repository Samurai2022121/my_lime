# Generated by Django 4.0.1 on 2022-02-15 12:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_alter_product_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='products/categories/', validators=[django.core.validators.FileExtensionValidator(['svg', 'png', 'jpg'])], verbose_name='Изображение категории'),
        ),
    ]
