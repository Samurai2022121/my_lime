from django.core.exceptions import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children', verbose_name='Родительская категория')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.FileField(blank=True, null=True, verbose_name="Изображение категории",
                              upload_to='products/categories/')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        ordering = ['name']
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Наименование')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL,
                                 verbose_name='Категория', null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    protein = models.FloatField(blank=True, null=True, verbose_name='Белки')
    carbohydrates = models.FloatField(blank=True, null=True, verbose_name='Углеводы')
    fats = models.FloatField(blank=True, null=True, verbose_name='Жиры')
    calories = models.FloatField(blank=True, null=True, verbose_name='Калорийность')
    energy = models.FloatField(blank=True, null=True, verbose_name='Энергетическая ценность')
    barcode = models.IntegerField(blank=True, null=True, verbose_name='Штрихкод')
    manufacturer = models.CharField(max_length=250, blank=True, null=True, verbose_name='Производитель')
    origin = models.CharField(max_length=50, blank=True, null=True, verbose_name='Страна происхождения')
    expiration_date = models.DateField(blank=True, null=True, verbose_name='Срок годности')
    production_date = models.DateField(blank=True, null=True, verbose_name='Дата производства')
    weight = models.FloatField(blank=True, null=True, verbose_name='Вес, грамм')
    in_stock = models.BooleanField(verbose_name='Наличие')
    own_production = models.BooleanField(default=False, verbose_name='Собственное производство')
    discount = models.IntegerField(blank=True, null=True, verbose_name='Скидка, %')
    extra_info = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ["manufacturer", "name"]
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Product, self).save()


class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    description = models.CharField(max_length=250, null=True, blank=True)
    image_1000 = models.ImageField(null=True, blank=True, upload_to="products/image_1000/",
                                   verbose_name='1000x1000, использовать для загрузки оригинала')
    image_500 = models.ImageField(null=True, blank=True, upload_to="products/image_500/", verbose_name='500x500')
    image_150 = models.ImageField(null=True, blank=True, upload_to="products/image_150/", verbose_name='150x150')
    main = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товара'

    def __str__(self):
        return self.product.name

    def save(self, *args, **kwargs):
        if self.main and not self.pk:
            if ProductImages.objects.filter(product=self.product, main=True).exists():
                raise ValidationError("У товара уже есть основное изображение.")
        super(ProductImages, self).save()
