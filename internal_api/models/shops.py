from decimal import Decimal

from django.contrib.postgres.expressions import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError

from discounts.models import Offer
from products.models import ProductUnit
from utils.models_utils import (
    ArrayJSONSubquery,
    LiteralJSONField,
    Timestampable,
    build_offer_subquery,
)


class Shop(models.Model):
    address = models.TextField(verbose_name="адрес")
    name = models.CharField(max_length=255, verbose_name="название")
    date_added = models.DateTimeField(auto_now=True, verbose_name="дата добавления")
    is_archive = models.BooleanField(default=False, verbose_name="архивный")
    e_shop_base = models.BooleanField(
        default=False, verbose_name="площадка интернет-магазина"
    )

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

    def __str__(self):
        return self.name


class WarehouseManager(models.Manager):
    """Apply margin on highest income record cost."""

    def get_queryset(self):
        qs = super().get_queryset()
        offer_qs = Offer.objects.filter(is_active=True, type=Offer.TYPES.site)
        return qs.annotate(
            recommended_price=(
                (models.F("margin") + Decimal(100))
                * models.Max(
                    "warehouse_records__cost",
                    filter=models.Q(warehouse_records__quantity__gt=Decimal(0)),
                )
                / Decimal(100)
            ),
            remaining=Coalesce(
                models.Sum("warehouse_records__quantity"),
                Decimal(0),
                output_field=models.DecimalField(max_digits=7, decimal_places=2),
            ),
            offers=ArrayJSONSubquery(
                build_offer_subquery(
                    build_offer_subquery(offer_qs, "benefit", "product_unit_id"),
                    "condition",
                    "product_unit_id",
                )
                .annotate(
                    condition_type=models.F("condition__type"),
                    condition_value=models.F("condition__value"),
                    benefit_type=models.F("benefit__type"),
                    benefit_value=models.F("benefit__value"),
                )
                .values(
                    "pk",
                    "condition_type",
                    "condition_value",
                    "benefit_type",
                    "benefit_value",
                ),
                output_field=ArrayField(
                    LiteralJSONField(),
                    verbose_name="скидки (упрощённый режим)",
                ),
            ),
        )


class Warehouse(models.Model):
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    min_remaining = models.DecimalField(
        "минимальный остаток",
        default=0,
        max_digits=9,
        decimal_places=4,
    )
    max_remaining = models.DecimalField(
        "максимальный остаток",
        default=0,
        max_digits=9,
        decimal_places=4,
    )
    margin = models.DecimalField(
        "наценка, %",
        blank=True,
        null=True,
        max_digits=6,
        decimal_places=2,
    )
    auto_order = models.BooleanField("автоматический заказ", default=False)
    price = models.DecimalField(
        "Цена",
        decimal_places=2,
        max_digits=6,
        validators=[MinValueValidator(0.01), MaxValueValidator(9999.99)],
    )

    objects = WarehouseManager()

    class Meta:
        verbose_name = "Запас"
        verbose_name_plural = "Запасы"
        default_related_name = "warehouses"
        constraints = (
            models.CheckConstraint(
                check=models.Q(price__gte=0.01) & models.Q(price__lte=9999.99),
                name="price_range",
            ),
            models.UniqueConstraint(
                fields=("shop", "product_unit"),
                name="unique_product_unit_and_shop",
            ),
        )

    def __str__(self):
        return f"{self.product_unit.unit} of {self.product_unit.product} in {self.shop}"


class BatchManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(created_at=models.Min("warehouse_records__created_at"))
        return qs


class Batch(models.Model):
    supplier = models.ForeignKey(
        "internal_api.Supplier",
        on_delete=models.PROTECT,
        verbose_name="поставщик",
        related_name="batches",
        blank=True,
        null=True,
    )
    expiration_date = models.DateField("годен до", blank=True, null=True)
    production_date = models.DateField("дата производства", blank=True, null=True)

    objects = BatchManager()

    class Meta:
        verbose_name = "партия"
        verbose_name_plural = "партии"
        default_related_name = "batches"

    def __str__(self):
        return f"Партия {self.id}"


class WarehouseRecordManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(
            vat_rate=models.ExpressionWrapper(
                models.F("warehouse__product_unit__product__vat_rate"),
                output_field=models.DecimalField(
                    "ставка НДС, %",
                    max_digits=7,
                    decimal_places=2,
                ),
            ),
            vat_value=models.ExpressionWrapper(
                models.F("quantity") * models.F("cost") * models.F("vat_rate") / 100,
                output_field=models.DecimalField(
                    "сумма НДС",
                    max_digits=7,
                    decimal_places=2,
                ),
            ),
        )


class WarehouseRecord(Timestampable, models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        verbose_name="партия",
        blank=True,
        null=True,
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        verbose_name="запас",
    )
    quantity = models.DecimalField(
        "количество",
        max_digits=9,
        decimal_places=4,
    )
    cost = models.DecimalField(
        "стоимость",
        null=True,
        blank=True,
        max_digits=7,
        decimal_places=2,
    )
    document = models.ForeignKey(
        "internal_api.PrimaryDocument",
        on_delete=models.CASCADE,
        verbose_name="первичный документ",
    )

    objects = WarehouseRecordManager()

    class Meta:
        verbose_name = "Изменение запаса"
        verbose_name_plural = "Изменения запаса"
        default_related_name = "warehouse_records"

    def __str__(self):
        return f"Изменение {self.warehouse}"

    def save(self, *args, **kwargs):
        if self.batch:
            product_units = self.batch.warehouse_records.values_list(
                "warehouse__product_unit",
                flat=True,
            )
            if product_units.count() > 1:
                raise ValidationError(f"{self.batch} is invalid")

            if product_units and self.warehouse.product_unit.id != product_units[0]:
                raise ValidationError(
                    f"{self.batch} represent only"
                    f" {self.batch.warehouse_records.first().warehouse.product_unit}"
                )

        super().save(*args, **kwargs)
