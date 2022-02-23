from datetime import date
from secrets import token_hex

from django.db import models

from products.models import ProductUnit
from utils.models_utils import Timestampable, phone_regex


class Shop(models.Model):
    address = models.TextField()
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now=True)
    is_archive = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Personnel(models.Model):
    WORK_STATUSES = (
        ("working", "Работает"),
        ("fired", "Уволен"),
        ("vacation", "Отпуск"),
        ("maternity_leave", "Декрет"),
        ("probation", "Исп. срок"),
    )

    is_archived = models.BooleanField(default=False)
    position = models.CharField(max_length=255)
    working_place = models.ForeignKey(Shop, on_delete=models.PROTECT)
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    date_hired = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=WORK_STATUSES)
    photo = models.ImageField(upload_to="internal-api/staff/", null=True, blank=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    passport = models.CharField(max_length=100)
    place_of_birth = models.CharField(max_length=255)
    department_issued_passport = models.CharField(max_length=255)
    identification_number = models.CharField(max_length=255)
    date_passport_issued = models.DateField()
    date_passport_valid = models.DateField()
    contract_period = models.IntegerField()
    contract_type = models.CharField(max_length=255)
    is_archive = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Персонал"
        verbose_name_plural = "Персонал"

    def __str__(self):
        return self.first_name


def create_personnel_document_download_path(instance, filename):
    directory = "internal-api/personal-documents/"
    upload_date = date.today().strftime("%d%M%Y")
    salt = token_hex(5)
    return f"{directory}_{upload_date}_{salt}_{filename}"


class PersonnelDocument(Timestampable, models.Model):
    personnel = models.ForeignKey(
        Personnel, on_delete=models.PROTECT, related_name="personnel_document"
    )
    personnel_document = models.FileField(
        upload_to=create_personnel_document_download_path, null=True
    )
    document_number = models.CharField(max_length=255)
    document_date = models.DateField()


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True
    )
    extra_info = models.JSONField(null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    bank_identifier_code = models.CharField(max_length=255, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    inner_id = models.CharField(max_length=255, null=True, blank=True)
    payer_identification_number = models.CharField(
        max_length=255, null=True, blank=True
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
    contract = models.FileField(upload_to=create_contract_download_path)
    contract_number = models.CharField(max_length=255)
    contract_date = models.DateField()

    class Meta:
        verbose_name = "Контракт поставщика"
        verbose_name_plural = "Контракты поставщиков"

    def __str__(self):
        return self.supplier.name


class Warehouse(models.Model):
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    min_remaining = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    max_remaining = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="warehouse",
    )
    margin = models.DecimalField(blank=True, null=True, max_digits=4, decimal_places=2)
    auto_order = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Запас"
        verbose_name_plural = "Запасы"
        default_related_name = "warehouses"

    def __str__(self):
        return f"{self.product_unit} in {self.shop}"


class PrimaryDocument(models.Model):
    created_at = models.DateField("создан", auto_now_add=True, editable=True)
    number = models.CharField("номер", max_length=255, unique=True)

    class Meta:
        verbose_name = "Документ первичного учёта"
        verbose_name_plural = "Документы первичного учёта"
        ordering = ("created_at", "number")

    def __str__(self):
        return f"{self.number} от {self.created_at}"


class ProductionDocument(PrimaryDocument):
    daily_menu_plan = models.ForeignKey(
        "production.DailyMenuPlan",
        on_delete=models.PROTECT,
        related_name="production_documents",
        verbose_name="план меню на день",
    )

    class Meta:
        verbose_name = "Документ учёта произведённой продукции"
        verbose_name_plural = "Документы учёта произведённой продукции"


class WarehouseRecord(Timestampable, models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        verbose_name="запас",
    )
    quantity = models.DecimalField("количество", max_digits=7, decimal_places=2)
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

    def __str__(self):
        return self.order_number


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
    margin = models.DecimalField(default=0, max_digits=4, decimal_places=2)

    class Meta:
        verbose_name = "Строка заказа"
        verbose_name_plural = "Строки заказа"
        default_related_name = "warehouse_order_positions"

    def __str__(self):
        return f"{self.product.name} in {self.warehouse_order}"


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
