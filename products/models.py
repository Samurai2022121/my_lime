from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from utils.models_utils import Timestampable


class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.FileField(
        blank=True,
        null=True,
        verbose_name="Изображение категории",
        upload_to="products/categories/",
        validators=[FileExtensionValidator(["svg", "png", "jpg"])],
    )
    is_archive = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        ordering = ["name"]
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(Timestampable, models.Model):
    name = models.CharField(max_length=250, verbose_name="Наименование")
    short_name = models.CharField(
        max_length=20, verbose_name="Краткое наименование", null=True, blank=True
    )
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        null=True,
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        verbose_name="Цена",
        validators=[MinValueValidator(0.01), MaxValueValidator(9999.99)],
    )
    protein = models.DecimalField(
        blank=True, null=True, verbose_name="Белки", max_digits=4, decimal_places=2
    )
    carbohydrates = models.DecimalField(
        blank=True, null=True, verbose_name="Углеводы", max_digits=4, decimal_places=2
    )
    fats = models.DecimalField(
        blank=True, null=True, verbose_name="Жиры", max_digits=4, decimal_places=2
    )
    calories = models.DecimalField(
        blank=True,
        null=True,
        verbose_name="Калорийность",
        max_digits=6,
        decimal_places=2,
    )
    energy = models.DecimalField(
        blank=True,
        null=True,
        verbose_name="Энергетическая ценность",
        max_digits=6,
        decimal_places=2,
    )
    barcode = models.BigIntegerField(blank=True, null=True, verbose_name="Штрихкод")
    manufacturer = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Производитель"
    )
    origin = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Страна происхождения"
    )
    expiration_date = models.DateField(
        blank=True, null=True, verbose_name="Срок годности"
    )
    production_date = models.DateField(
        blank=True, null=True, verbose_name="Дата производства"
    )
    weight = models.DecimalField(
        blank=True, null=True, verbose_name="Вес, грамм", max_digits=7, decimal_places=2
    )
    in_stock = models.BooleanField(verbose_name="Наличие", default=False)
    own_production = models.BooleanField(
        default=False, verbose_name="Собственное производство"
    )
    discount = models.DecimalField(
        blank=True, null=True, verbose_name="Скидка, %", max_digits=5, decimal_places=2
    )
    extra_info = models.JSONField(null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    is_sorted = models.BooleanField(default=False)
    vat_value = models.DecimalField(
        null=True, blank=True, max_digits=7, decimal_places=2
    )
    for_scales = models.BooleanField(default=False)
    for_own_production = models.BooleanField(default=False)

    class Meta:
        unique_together = ["manufacturer", "name", "barcode"]
        verbose_name = "товар"
        verbose_name_plural = "товары"
        constraints = (
            models.CheckConstraint(
                check=models.Q(price__gte=0.01) & models.Q(price__lte=9999.99),
                name="price_range",
            ),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Product, self).save()

    def clean(self):
        if self.for_scales and (not self.short_name or not self.category):
            raise ValidationError(_("Обязательны параметры short_name и category."))


class MeasurementUnit(models.Model):
    name = models.CharField("наименование", max_length=255, unique=True)

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="units",
    )
    unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        related_name="product_units",
    )
    for_resale = models.BooleanField("допустима продажа", default=True)

    class Meta:
        verbose_name = "Единица хранения"
        verbose_name_plural = "Единицы хранения"

    def __str__(self):
        return f"{self.unit} of {self.product}"


class ProductUnitConversion(models.Model):
    source_unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.CASCADE,
        related_name="conversion_sources",
        verbose_name="из",
    )
    target_unit = models.ForeignKey(
        ProductUnit,
        on_delete=models.CASCADE,
        related_name="conversion_targets",
        verbose_name="в",
    )
    factor = models.DecimalField(
        "множитель",
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Перевод единиц хранения"
        verbose_name_plural = "Переводы единиц хранения"
        unique_together = ("source_unit", "target_unit")

    def __str__(self):
        return (
            f"{self.source_unit.product.name}:"
            f" 1 {self.source_unit.unit.name} ="
            f" {self.factor} {self.target_unit.unit.name}"
        )


class ProductImages(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    description = models.CharField(max_length=250, null=True, blank=True)
    image_1000 = models.ImageField(
        null=True,
        blank=True,
        upload_to="products/image_1000/",
        verbose_name="1000x1000, использовать для загрузки оригинала",
    )
    image_500 = models.ImageField(
        null=True, blank=True, upload_to="products/image_500/", verbose_name="500x500"
    )
    image_150 = models.ImageField(
        null=True, blank=True, upload_to="products/image_150/", verbose_name="150x150"
    )
    main = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"

    def __str__(self):
        return self.product.name

    def save(self, *args, **kwargs):
        if self.main and not self.pk:
            if ProductImages.objects.filter(product=self.product, main=True).exists():
                raise ValidationError("У товара уже есть основное изображение.")
        super(ProductImages, self).save()
