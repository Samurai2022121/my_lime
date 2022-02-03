from datetime import date
from secrets import token_hex

from django.db import models

from products.models import Product
from utils.models_utils import Timestampable, phone_regex


class Shop(models.Model):
    address = models.TextField()
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now=True)
    is_archive = models.BooleanField(default=False)


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
        upload_to=create_personnel_document_download_path
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
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="warehouse"
    )
    shop = models.PositiveIntegerField(db_index=True)
    remaining = models.FloatField(default=0, blank=True, null=True)
    min_remaining = models.FloatField(default=0, blank=True, null=True)
    max_remaining = models.FloatField(default=0, blank=True, null=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="warehouse",
    )
    margin = models.FloatField(blank=True, null=True)
    auto_order = models.BooleanField(default=False)


class RemainingProduct(Timestampable, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="remaining_product"
    )
    remaining = models.FloatField(default=1)


class TechCard(Timestampable, models.Model):
    name = models.CharField(max_length=255)
    amount = models.FloatField(default=1)
    author = models.ForeignKey(
        Personnel, on_delete=models.PROTECT, related_name="tech_card"
    )
    is_archive = models.BooleanField(default=False)
    product = models.ManyToManyField(Product, through="TechCardProduct")

    class Meta:
        verbose_name = "Техкарта"
        verbose_name_plural = "Техкарты"

    def __str__(self):
        return self.name


class TechCardProduct(models.Model):
    tech_card = models.ForeignKey(
        TechCard, on_delete=models.PROTECT, related_name="tech_product"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="tech_card_product"
    )
    quantity = models.FloatField()


class DailyMenuPlan(Timestampable, models.Model):
    dishes = models.ManyToManyField(TechCard, through="MenuDish")
    author = models.ForeignKey(
        Personnel, on_delete=models.PROTECT, related_name="daily_menu_plan"
    )

    class Meta:
        verbose_name = "План меню на день"
        verbose_name_plural = "Планы меню на день"

    def __str__(self):
        return self.author.first_name


class MenuDish(models.Model):
    dish = models.ForeignKey(
        TechCard, on_delete=models.PROTECT, related_name="menu_dish"
    )
    menu = models.ForeignKey(
        DailyMenuPlan,
        on_delete=models.PROTECT,
        related_name="menu_dish",
    )
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Заявка меню на день"
        verbose_name_plural = "Заявки меню на день"

    def __str__(self):
        return self.dish.name


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
        related_name="warehouse_order",
    )
    order_positions = models.ManyToManyField(
        Product, through="WarehouseOrderPositions", blank=True
    )
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    waybill = models.CharField(max_length=255, null=True, blank=True)
    waybill_date = models.DateField(null=True, blank=True)
    order_number = models.CharField(max_length=255, null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True)


class WarehouseOrderPositions(models.Model):
    warehouse_order = models.ForeignKey(
        WarehouseOrder, on_delete=models.PROTECT, related_name="warehouse_order"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="warehouse_order_product"
    )
    quantity = models.FloatField(default=0)
    bonus = models.IntegerField(default=0)
    special = models.FloatField(default=0)
    flaw = models.FloatField(default=0)
    buying_price = models.FloatField(default=0)
    value_added_tax = models.FloatField(default=0)
    value_added_tax_value = models.FloatField(default=0)
    margin = models.FloatField(default=0)
