from datetime import date
from decimal import Decimal
from secrets import token_hex

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce
from model_utils.managers import InheritanceManager

from products.models import ProductUnit
from utils.models_utils import Timestampable, classproperty, phone_regex


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


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="название")
    address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="адрес"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="email")
    phone_numbers = ArrayField(
        models.CharField(
            "номер телефона",
            validators=[phone_regex],
            max_length=17,
        ),
        verbose_name="номера телефонов",
        blank=True,
        default=list,
    )
    payment_deferral = models.PositiveIntegerField(
        "отсрочка оплаты, дней",
        default=0,
    )
    extra_info = models.JSONField(
        null=True, blank=True, verbose_name="дополнительная информация"
    )
    is_archive = models.BooleanField(default=False, verbose_name="архивный")
    bank_identifier_code = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="БИК"
    )
    bank_account = models.CharField(
        "номер банковского счета",
        max_length=255,
        null=True,
        blank=True,
    )
    inner_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="внутренний ID"
    )
    taxpayer_identification_number = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="ИНН"
    )

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name


def create_contract_download_path(instance, filename):
    directory = "internal-api/supply-contracts/"
    upload_date = date.today().strftime("%d%M%Y")
    salt = token_hex(5)
    return f"{directory}_{upload_date}_{salt}_{filename}"


class SupplyContract(Timestampable, models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name="supply_contract"
    )
    contract = models.FileField(
        upload_to=create_contract_download_path, verbose_name="контракт"
    )
    contract_number = models.CharField(max_length=255, verbose_name="номер контракта")
    contract_date = models.DateField(verbose_name="дата контракта")

    class Meta:
        verbose_name = "Контракт поставщика"
        verbose_name_plural = "Контракты поставщиков"

    def __str__(self):
        return self.supplier.name


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
        Supplier,
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


class PrimaryDocument(models.Model):
    NUMBER_DIGITS = 8
    NUMBER_PREFIX = ""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="автор",
    )
    created_at = models.DateField("создан", auto_now_add=True, editable=True)
    number = models.CharField("номер", max_length=255, unique=True, blank=True)

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

    def save(self, *args, **kwargs):
        # if a number is not provided, generate one
        if self.pk is None and not self.number:
            new_number = 1
            for latest_number in (
                self._meta.model.objects.filter(
                    number__startswith=self.NUMBER_PREFIX,
                )
                .order_by("-number")
                .values_list("number", flat=True)
                .iterator(chunk_size=1)
            ):
                try:
                    new_number = int(latest_number.lstrip(self.NUMBER_PREFIX)) + 1
                    break
                except ValueError:
                    pass

            self.number = self.NUMBER_PREFIX + str(new_number).zfill(self.NUMBER_DIGITS)
        super().save(*args, **kwargs)


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
        PrimaryDocument,
        on_delete=models.CASCADE,
        verbose_name="первичный документ",
    )

    class Meta:
        verbose_name = "Изменение запаса"
        verbose_name_plural = "Изменения запаса"
        default_related_name = "warehouse_records"

    def __str__(self):
        return f"Изменение {self.warehouse}"


class WarehouseOrder(models.Model):
    ORDER_STATUSES = (
        ("approving", "Подтверждается"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
        ("dispatched", "Отправлен"),
    )

    status = models.CharField(max_length=255, choices=ORDER_STATUSES)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="warehouse_orders",
    )
    order_positions = models.ManyToManyField(
        ProductUnit, through="WarehouseOrderPositions", blank=True
    )
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    waybill = models.CharField(max_length=255, null=True, blank=True)
    waybill_date = models.DateField(null=True, blank=True)
    order_number = models.CharField(max_length=255, null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.order_number or "-"


class WarehouseOrderPositions(models.Model):
    warehouse_order = models.ForeignKey(
        WarehouseOrder,
        on_delete=models.PROTECT,
    )
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    quantity = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    bonus = models.IntegerField(default=0)
    special = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    flaw = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    buying_price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    value_added_tax = models.DecimalField(default=0, max_digits=4, decimal_places=2)
    value_added_tax_value = models.DecimalField(
        default=0, max_digits=7, decimal_places=2
    )
    margin = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = "Строка заказа"
        verbose_name_plural = "Строки заказа"
        default_related_name = "warehouse_order_positions"

    def __str__(self):
        return f"{self.product_unit.product.name} in {self.warehouse_order}"


class LegalEntities(models.Model):
    registration_id = models.CharField(
        "регистрационный номер",
        max_length=9,
        primary_key=True,
    )
    registration_date = models.CharField(
        "дата регистрации",
        max_length=255,
        blank=True,
        null=True,
    )
    active = models.CharField(
        "действует",
        max_length=255,
        blank=True,
        null=True,
    )
    phone = models.CharField("телефон", max_length=255, blank=True, null=True)
    region = models.CharField("регион", max_length=255, blank=True, null=True)
    email = models.CharField("имейл", max_length=255, blank=True, null=True)
    address = models.CharField("адрес", max_length=255, blank=True, null=True)
    okved = models.CharField("ОКВЭД", max_length=255, blank=True, null=True)
    name = models.CharField(
        "краткое наименование",
        max_length=255,
        blank=True,
        null=True,
    )
    full_name = models.CharField(
        "полное наименование",
        max_length=255,
        blank=True,
        null=True,
    )
    status = models.CharField("статус", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Юридическое лицо"
        verbose_name_plural = "Юридические лица"
        db_table = "legal_entities"
        managed = False

    def __str__(self):
        return self.name
