from datetime import date
from secrets import token_hex

from django.contrib.postgres.fields import ArrayField
from django.db import models

from products.models import ProductUnit
from utils.models_utils import Enumerable, Timestampable, phone_regex


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


class WarehouseOrder(Enumerable):
    NUMBER_PREFIX = "AO"
    ORDER_STATUSES = (
        ("approving", "Подтверждается"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
        ("dispatched", "Отправлен"),
    )

    status = models.CharField(max_length=255, choices=ORDER_STATUSES)
    supplier = models.ForeignKey(
        "internal_api.Supplier",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="warehouse_orders",
    )
    order_positions = models.ManyToManyField(
        ProductUnit, through="WarehouseOrderPositions", blank=True
    )
    shop = models.ForeignKey("internal_api.Shop", on_delete=models.PROTECT)
    is_archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.number


class WarehouseOrderPositions(models.Model):
    warehouse_order = models.ForeignKey(
        WarehouseOrder,
        on_delete=models.PROTECT,
    )
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    quantity = models.DecimalField(default=0, max_digits=9, decimal_places=4)
    bonus = models.IntegerField(default=0)
    special = models.DecimalField(default=0, max_digits=9, decimal_places=4)
    flaw = models.DecimalField(default=0, max_digits=9, decimal_places=4)
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
