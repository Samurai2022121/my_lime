from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', verbose_name='Родительская категория')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        ordering = ['name']
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class ProductImages(models.Model):
    image = models.ImageField(null=True, blank=True)


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Наименование')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL,
                                 verbose_name='Категория', null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    main_image = models.ImageField(verbose_name='Основное изображение')
    images = models.ForeignKey(ProductImages, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='product', verbose_name='Изображения товара')
    protein = models.FloatField(blank=True, null=True, verbose_name='Белки')
    carbohydrates = models.FloatField(blank=True, null=True, verbose_name='Углеводы')
    fats = models.FloatField(blank=True, null=True, verbose_name='Жиры')
    calories = models.FloatField(blank=True, null=True, verbose_name='Калорийность')
    barcode = models.IntegerField(blank=True, null=True, verbose_name='Штрихкод')
    manufacturer = models.CharField(max_length=250, blank=True, null=True, verbose_name='Производитель')
    origin = models.CharField(max_length=50, blank=True, null=True, verbose_name='Страна происхождения')
    expiration_date = models.DateField(blank=True, null=True, verbose_name='Срок годности')
    weight = models.FloatField(blank=True, null=True, verbose_name='Вес (грамм)')
    in_stock = models.BooleanField(verbose_name='Наличие')
    own_production = models.BooleanField(default=False, verbose_name='Собственное производство')

    class Meta:
        unique_together = ["manufacturer", "name"]
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name
