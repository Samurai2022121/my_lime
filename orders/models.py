from django.conf import settings
from django.db import models
from model_utils.managers import InheritanceManager, InheritanceManagerMixin

from discounts.models import Offer
from internal_api.models.shops import Batch, Warehouse
from internal_api.models.shops import (
    WarehouseRecordManager as BaseWarehouseRecordManager,
)
from internal_api.models.shops import validate_batch
from utils.choices import Choices
from utils.models_utils import Enumerable, SuperclassMixin, Timestampable


class PrimaryDocument(SuperclassMixin, Enumerable):
    """
    This model is defined here and not imported from `internal_api.models`
    for the `author` field to be aliased as `buyer`.
    """

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_column="author_id",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="покупатель",
        related_name="orders",
    )
    created_at = models.DateField("создан", auto_now_add=True, editable=True)

    objects = InheritanceManager()

    class Meta:
        db_table = "internal_api_primarydocument"
        managed = False
        ordering = ("created_at", "number")

    def __str__(self):
        return f"{self.number} от {self.created_at}"


class SingleShopDocumentManager(models.Manager):
    """Annotate a document with the shop fk, if applicable (or null)."""

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            shop_count=models.Count(
                "lines__warehouse__shop",
                distinct=True,
            ),
            shop=models.Case(
                models.When(
                    shop_count=1,
                    then=models.F("lines__warehouse__shop"),
                ),
                default=None,
            ),
        )
        return qs


class Order(PrimaryDocument):
    NUMBER_PREFIX = "OR"
    STATUSES = Choices(
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("in-transit", "В пути"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    )
    PAYMENT_METHODS = Choices(
        ("card-pre", "Картой на сайте"),
        ("card-post", "Картой курьеру"),
        ("cash", "Наличные курьеру"),
    )

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="e_shop_order",
    )
    status = models.CharField(
        "статус",
        max_length=15,
        choices=STATUSES,
        default=STATUSES.new,
    )
    payment_method = models.CharField(
        "способ оплаты",
        max_length=15,
        choices=PAYMENT_METHODS,
    )
    buyer_comment = models.TextField("примечание покупателя", null=True, blank=True)
    staff_comment = models.TextField("примечание исполнителя", null=True, blank=True)

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"
        default_related_name = "orders"

    def __str__(self):
        return f"Заказ №{self.number} от {self.created_at}"


class WarehouseRecordManager(InheritanceManagerMixin, BaseWarehouseRecordManager):
    pass


class WarehouseRecord(Timestampable, models.Model):
    """
    This model is defined here and not imported from `internal_api.models`
    for the `cost` field to be aliased as `discounted_price`.
    """

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
    discounted_price = models.DecimalField(
        "цена со скидками",
        db_column="cost",
        null=True,
        blank=True,
        max_digits=7,
        decimal_places=2,
    )
    document = models.ForeignKey(
        PrimaryDocument,
        on_delete=models.CASCADE,
        verbose_name="первичный документ",
    )

    objects = WarehouseRecordManager()

    class Meta:
        db_table = "internal_api_warehouserecord"
        managed = False
        default_related_name = "lines"

    def __str__(self):
        return f"Изменение {self.warehouse}"

    def save(self, *args, **kwargs):
        validate_batch(self)
        super().save(*args, **kwargs)


class OrderLine(WarehouseRecord):
    warehouse_record = models.OneToOneField(
        WarehouseRecord,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="order_line",
    )
    full_price = models.DecimalField(
        "цена",
        null=True,
        blank=True,
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "строка заказа"
        verbose_name_plural = "строки заказа"


class OrderLineOffer(models.Model):
    line = models.ForeignKey(
        OrderLine,
        on_delete=models.CASCADE,
        related_name="offers",
        verbose_name="строка заказа",
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.PROTECT,
        related_name="order_line_offers",
        verbose_name="скидка",
    )
    apply_times = models.PositiveIntegerField("число применений")

    class Meta:
        verbose_name = "применённая скидка"
        verbose_name_plural = "применённые скидки"
