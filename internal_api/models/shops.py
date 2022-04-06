from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce

from products.models import ProductUnit
from utils.models_utils import Timestampable


class Shop(models.Model):
    address = models.TextField(verbose_name="адрес")
    name = models.CharField(max_length=255, verbose_name="название")
    date_added = models.DateTimeField(auto_now=True, verbose_name="дата добавления")
    is_archive = models.BooleanField(default=False, verbose_name="архивный")

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

    def __str__(self):
        return self.name


class WarehouseManager(models.Manager):
    """Apply margin on highest income record cost."""

    def get_queryset(self):
        qs = super().get_queryset()
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
        )


class Warehouse(models.Model):
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    min_remaining = models.DecimalField(
        default=0, max_digits=7, decimal_places=2, verbose_name="минимальный остаток"
    )
    max_remaining = models.DecimalField(
        default=0, max_digits=7, decimal_places=2, verbose_name="максимальный остаток"
    )
    supplier = models.ForeignKey(
        "internal_api.Supplier",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="warehouse",
    )
    margin = models.DecimalField(
        "наценка, %",
        blank=True,
        null=True,
        max_digits=6,
        decimal_places=2,
    )
    auto_order = models.BooleanField(default=False, verbose_name="автоматический заказ")
    price = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        verbose_name="Цена",
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
        )

    def __str__(self):
        return f"{self.product_unit} in {self.shop}"


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
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        verbose_name="запас",
    )
    quantity = models.DecimalField(
        "количество",
        max_digits=7,
        decimal_places=2,
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
