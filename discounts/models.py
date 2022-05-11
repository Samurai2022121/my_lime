import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from model_utils.choices import Choices


class Range(models.Model):
    include_product_units = models.ManyToManyField(
        "products.ProductUnit",
        verbose_name="действует на товарные единицы",
        related_name="include_ranges",
        blank=True,
    )
    include_products = models.ManyToManyField(
        "products.Product",
        verbose_name="действует на товары",
        related_name="include_ranges",
        blank=True,
    )
    include_categories = models.ManyToManyField(
        "products.Category",
        verbose_name="действует на категории товаров",
        related_name="include_ranges",
        blank=True,
    )
    exclude_product_units = models.ManyToManyField(
        "products.ProductUnit",
        verbose_name="не действует на товарные единицы",
        related_name="exclude_ranges",
        blank=True,
    )
    exclude_products = models.ManyToManyField(
        "products.Product",
        verbose_name="не действует на товары",
        related_name="exclude_ranges",
        blank=True,
    )
    exclude_categories = models.ManyToManyField(
        "products.Category",
        verbose_name="не действует на категории товаров",
        related_name="exclude_ranges",
        blank=True,
    )
    includes_all = models.BooleanField(
        "действует на все продукты",
        default=False,
    )
    name = models.CharField("название", unique=True, max_length=128)

    class Meta:
        verbose_name = "диапазон товаров"
        verbose_name_plural = "диапазоны товаров"

    def __str__(self):
        return self.name


class Condition(models.Model):
    TYPES = Choices(
        ("count", "общее количество товаров из выборки"),
        ("value", "товаров из выборки на сумму"),
        ("coverage", "число отдельных товаров из выборки"),
    )

    range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        verbose_name="диапазоны товаров",
        related_name="conditions",
    )
    type = models.CharField("тип", choices=TYPES, default=TYPES.count, max_length=16)
    value = models.DecimalField(
        "значение", max_digits=9, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        verbose_name = "условие"
        verbose_name_plural = "условия"

    def __str__(self):
        return f"{self.range.name}: {self.type}: {self.value}"


class Benefit(models.Model):
    TYPES = Choices(
        ("percentage", "скидка на выбранные товары, %"),
        ("absolute", "скидка на выбранные товары, сумма"),
        ("multibuy", "самый недорогой из выбранных товаров -- бесплатно"),
        ("fixed-price", "стоимость всех выбранных товаров"),
    )

    range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        verbose_name="диапазоны товаров",
        related_name="benefits",
    )
    type = models.CharField(
        "тип", choices=TYPES, default=TYPES.percentage, max_length=16
    )
    value = models.DecimalField(
        "значение", max_digits=9, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        verbose_name = "выгода"
        verbose_name_plural = "выгоды"

    def __str__(self):
        return f"{self.range.name}: {self.type}: {self.value}"


def in_a_month():
    return timezone.now() + timedelta(days=30)


class Offer(models.Model):
    TYPES = Choices(
        ("site", "доступно для всех"),
        ("voucher", "доступно по одноразовому коду"),
        ("loyalty", "доступно по карте клиента"),
        ("buyer", "доступно зарегистрированным пользователям"),
    )

    condition = models.OneToOneField(
        Condition,
        on_delete=models.CASCADE,
        related_name="offer",
        verbose_name="условие",
    )
    benefit = models.OneToOneField(
        Benefit,
        on_delete=models.CASCADE,
        related_name="offer",
        verbose_name="выгода",
    )
    name = models.CharField("название", unique=True, max_length=128)
    description = models.TextField("описание", null=True, blank=True)
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    is_public = models.BooleanField("открыто", default=True)
    is_active = models.BooleanField("активно", default=True)
    type = models.CharField("тип", choices=TYPES, default=TYPES.site, max_length=16)
    started_at = models.DateTimeField("доступно с", default=timezone.now)
    ended_at = models.DateTimeField("доступно до", default=in_a_month)
    order_limit = models.PositiveBigIntegerField(
        "использовать в одной продаже не более, раз", default=0
    )
    site_limit = models.PositiveBigIntegerField("использовать не более, раз", default=0)
    buyer_limit = models.PositiveBigIntegerField(
        "использовать одному покупателю не более, раз", default=0
    )
    application_count = models.PositiveBigIntegerField("использовано, раз", default=0)

    class Meta:
        verbose_name = "предложение"
        verbose_name_plural = "предложения"
        ordering = ("created_at",)

    def __str__(self):
        return self.name


class BuyerCount(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="покупатель",
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        verbose_name="предложение",
    )
    application_count = models.PositiveBigIntegerField("использовано, раз", default=0)

    class Meta:
        verbose_name = "использование предложения"
        verbose_name_plural = "использования предложения"
        default_related_name = "buyer_counts"
        unique_together = ("buyer", "offer")


class LoyaltyCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    is_active = models.BooleanField("активно", default=True)
    buyer = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="покупатель",
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        verbose_name="предложение",
    )
    application_count = models.PositiveBigIntegerField("использовано, раз", default=0)

    class Meta:
        verbose_name = "Программа лояльности"
        verbose_name_plural = "Программа лояльности"
        default_related_name = "loyalty_cards"

    def __str__(self):
        return self.id


class Voucher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    is_active = models.BooleanField("активно", default=True)
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        verbose_name="предложение",
        related_name="vouchers",
    )

    class Meta:
        verbose_name = "ваучер"
        verbose_name_plural = "ваучеры"

    def __str__(self):
        return self.id
