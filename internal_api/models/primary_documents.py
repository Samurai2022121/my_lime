from django.conf import settings
from django.db import models
from model_utils.managers import InheritanceManager

from utils.models_utils import Enumerable, classproperty

from .shops import WarehouseRecord


class SingleShopDocumentManager(models.Manager):
    """Annotate a document with the shop fk, if applicable (or null)."""

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            shop_count=models.Count(
                "warehouse_records__warehouse__shop",
                distinct=True,
            ),
            shop=models.Case(
                models.When(
                    shop_count=1,
                    then=models.F("warehouse_records__warehouse__shop"),
                ),
                default=None,
            ),
        )
        return qs


class MoveDocumentManager(models.Manager):
    """Annotate a document with source and target shop fks."""

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            source_shop_count=models.Count(
                "warehouse_records__warehouse__shop",
                filter=models.Q(warehouse_records__quantity__lt=0),
                distinct=True,
            ),
            source_shop=models.Case(
                models.When(
                    source_shop_count=1,
                    then=models.Subquery(
                        WarehouseRecord.objects.filter(
                            document=models.OuterRef("pk"),
                            quantity__lt=0,
                        ).values("warehouse__shop"),
                    ),
                ),
                default=None,
            ),
            target_shop_count=models.Count(
                "warehouse_records__warehouse__shop",
                filter=models.Q(warehouse_records__quantity__gt=0),
                distinct=True,
            ),
            target_shop=models.Case(
                models.When(
                    target_shop_count=1,
                    then=models.Subquery(
                        WarehouseRecord.objects.filter(
                            document=models.OuterRef("pk"),
                            quantity__gt=0,
                        ).values("warehouse__shop"),
                    ),
                ),
                default=None,
            ),
        )
        return qs


class PrimaryDocument(Enumerable):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="автор",
    )
    created_at = models.DateField("создан", auto_now_add=True, editable=True)

    objects = InheritanceManager()

    class Meta:
        verbose_name = "Документ первичного учёта"
        verbose_name_plural = "Документы первичного учёта"
        ordering = ("created_at", "number")

    def __str__(self):
        return f"{self.number} от {self.created_at}"

    @classproperty
    @classmethod
    def SUBCLASS_OBJECT_CHOICES(cls):
        """All known subclasses, keyed by a unique name per class."""
        return {
            rel.name: rel.related_model
            for rel in cls._meta.related_objects
            if rel.parent_link
        }

    @classproperty
    @classmethod
    def SUBCLASS_CHOICES(cls):
        """Available subclass choices, with nice names."""
        return [
            (name, model._meta.verbose_name)
            for name, model in cls.SUBCLASS_OBJECT_CHOICES.items()
        ]

    @classmethod
    def SUBCLASS(cls, name):
        """Given a subclass name, return the subclass."""
        return cls.SUBCLASS_OBJECT_CHOICES.get(name, cls)


class ProductionDocument(PrimaryDocument):
    NUMBER_PREFIX = "PR"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="production_document",
    )
    daily_menu_plan = models.ForeignKey(
        "production.DailyMenuPlan",
        on_delete=models.PROTECT,
        related_name="production_documents",
        verbose_name="план меню на день",
    )

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "Документ учёта произведённой продукции"
        verbose_name_plural = "Документы учёта произведённой продукции"


class InventoryDocument(PrimaryDocument):
    NUMBER_PREFIX = "IV"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="inventory_document",
    )

    class Meta:
        verbose_name = "Остаток на начало периода"
        verbose_name_plural = "Остатки на начало периода"


class WriteOffDocument(PrimaryDocument):
    NUMBER_PREFIX = "WR"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="write_off_document",
    )
    reason = models.TextField("причина", null=True, blank=True)

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "Документ списания"
        verbose_name_plural = "Документы списания"


class ConversionDocument(PrimaryDocument):
    NUMBER_PREFIX = "CV"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="conversion_document",
    )

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "Документ перевода единиц хранения"
        verbose_name_plural = "Документы перевода единиц хранения"


class MoveDocument(PrimaryDocument):
    NUMBER_PREFIX = "MV"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="move_document",
    )

    objects = MoveDocumentManager()

    class Meta:
        verbose_name = "Документ перемещения"
        verbose_name_plural = "Документы перемещения"


class ReceiptDocument(PrimaryDocument):
    NUMBER_PREFIX = "RC"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="receipt_document",
    )
    order = models.ForeignKey(
        "internal_api.WarehouseOrder",
        on_delete=models.PROTECT,
        related_name="receipts",
        verbose_name="заказ",
    )
    waybill = models.CharField(
        "номер накладной",
        max_length=255,
        null=True,
        blank=True,
    )
    waybill_date = models.DateField("дата накладной", null=True, blank=True)

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "Документ поступления товара"
        verbose_name_plural = "Документы поступления товара"


class SaleDocument(PrimaryDocument):
    NUMBER_PREFIX = "SL"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="sale_document",
    )

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "Документ продажи"
        verbose_name_plural = "Документы продажи"


class CancelDocument(PrimaryDocument):
    NUMBER_PREFIX = "CN"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="cancel_document",
    )
    cancels = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.PROTECT,
        related_name="cancelled_by",
        verbose_name="отменяет",
    )
    reason = models.TextField("причина", null=True, blank=True)

    class Meta:
        verbose_name = "Документ отмены"
        verbose_name_plural = "Документы отмены"


class ReturnDocument(PrimaryDocument):
    NUMBER_PREFIX = "RT"

    primary_document = models.OneToOneField(
        PrimaryDocument,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name="return_document",
    )
    reason = models.TextField("причина", null=True, blank=True)

    objects = SingleShopDocumentManager()

    class Meta:
        verbose_name = "Документ возврата"
        verbose_name_plural = "Документы возврата"
