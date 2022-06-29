from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint
from mptt.models import MPTTModel, TreeForeignKey
from sorl.thumbnail.fields import ImageField

from utils.models_utils import Timestampable
from utils.thumbnail import resize_image


class Category(MPTTModel):
    name = models.CharField(max_length=50, verbose_name="Название")
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
        constraints = (
            UniqueConstraint(
                fields=("name", "parent"),
                name="unique_name",
            ),
            UniqueConstraint(
                fields=("name",),
                condition=models.Q(parent=None),
                name="unique_root_name",
            ),
        )

    def __str__(self):
        return self.name


class Product(Timestampable, models.Model):
    name = models.CharField(max_length=250, verbose_name="Наименование")
    short_name = models.CharField(
        max_length=20, verbose_name="Краткое наименование", null=True, blank=True
    )
    category = TreeForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    protein = models.DecimalField(
        blank=True, null=True, verbose_name="Белки", max_digits=5, decimal_places=2
    )
    carbohydrates = models.DecimalField(
        blank=True, null=True, verbose_name="Углеводы", max_digits=5, decimal_places=2
    )
    fats = models.DecimalField(
        blank=True, null=True, verbose_name="Жиры", max_digits=5, decimal_places=2
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
    manufacturer = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Производитель"
    )
    origin = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Страна происхождения"
    )
    own_production = models.BooleanField(
        default=False, verbose_name="Собственное производство"
    )
    discount = models.DecimalField(
        blank=True, null=True, verbose_name="Скидка, %", max_digits=5, decimal_places=2
    )
    extra_info = models.JSONField(
        "дополнительная информация",
        null=True,
        blank=True,
    )
    is_archive = models.BooleanField("в архиве", default=False)
    is_sorted = models.BooleanField(
        "завизировано после автоматического добавления",
        default=False,
    )
    vat_rate = models.DecimalField(
        "Ставка НДС, %",
        null=True,
        blank=True,
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name


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
    for_scales = models.BooleanField("весовой товар", default=False)
    for_weighing_scales = models.BooleanField("для чекопечатающих весов", default=False)
    barcode = models.BigIntegerField("штрихкод", blank=True, null=True)
    weight = models.DecimalField(
        "вес с упаковкой, г",
        blank=True,
        null=True,
        max_digits=9,
        decimal_places=4,
    )
    packing_weight = models.DecimalField(
        "вес упаковки, г",
        blank=True,
        null=True,
        max_digits=9,
        decimal_places=4,
    )

    class Meta:
        verbose_name = "Единица хранения"
        verbose_name_plural = "Единицы хранения"

    def __str__(self):
        return f"{self.unit} of {self.product}"

    def save(self, *args, **kwargs):
        if self.for_scales:
            if not self.product.short_name:
                raise ValidationError(
                    {
                        "for_scales": "Весовой товар должен иметь краткое наименование.",
                    }
                )
            if not self.product.category:
                raise ValidationError(
                    {
                        "for_scales": "Весовой товар должен иметь категорию.",
                    }
                )
        super().save(*args, **kwargs)


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


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар",
    )
    description = models.CharField(max_length=250, null=True, blank=True)
    image = ImageField(
        null=True,
        blank=True,
        upload_to="products/image_1000/",
        verbose_name="оригинал изображения",
    )
    main = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"
        constraints = (
            UniqueConstraint(
                fields=("product", "main"),
                name="one_main_image_per_product",
                condition=models.Q(main=True),
            ),
        )

    def __str__(self):
        return Path(self.image.name).name

    def save(self, *args, **kwargs):
        is_created = not self.pk
        super().save(*args, **kwargs)
        if is_created and not settings.PRODUCT_IMAGE_PRESERVE_ORIGINAL:
            resize_image(self.image.path)
