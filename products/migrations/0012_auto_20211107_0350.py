# Generated by Django 3.2.4 on 2021-11-07 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20211107_0253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productimages',
            options={'verbose_name': 'Изображение товара', 'verbose_name_plural': 'Изображения товара'},
        ),
        migrations.AlterField(
            model_name='productimages',
            name='description',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='productimages',
            name='image_1000',
            field=models.ImageField(blank=True, null=True, upload_to='products/image_1000/', verbose_name='1000x1000, использовать для загрузки оригинала'),
        ),
        migrations.AlterField(
            model_name='productimages',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product', verbose_name='Товар'),
        ),
    ]
