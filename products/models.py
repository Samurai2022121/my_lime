from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True, default=name)
    specification = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Наименование')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    image = models.ImageField(verbose_name='Изображение')
    protein = models.FloatField(blank=True, null=True, verbose_name='Белки')
    carbs = models.FloatField(blank=True, null=True, verbose_name='Углеводы')
    fats = models.FloatField(blank=True, null=True, verbose_name='Жиры')
    calories = models.FloatField(blank=True, null=True, verbose_name='Калорийность')
    barcode = models.IntegerField(blank=True, null=True, verbose_name='Штрихкод')
    manufacturer = models.CharField(max_length=150, blank=True, null=True, verbose_name='Производитель')
    origin = models.CharField(max_length=50, blank=True, null=True, verbose_name='Страна происхождения')
    expiration_date = models.DateField(blank=True, null=True, verbose_name='Срок годности')
    weight = models.FloatField(blank=True, null=True, verbose_name='Вес')
    in_stock = models.BooleanField(verbose_name='Наличие')

    class Meta:
        unique_together = ("manufacturer", "name")
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name
