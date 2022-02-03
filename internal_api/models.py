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
    contract_number = models.CharField(max_length=255)
    contract_date = models.DateField()

    class Meta:
        verbose_name = "Контракт поставщика"
        verbose_name_plural = "Контракты поставщиков"

    def __str__(self):
        return self.supplier.name


class SupplyContractFile(models.Model):
    contract = models.FileField(upload_to=create_contract_download_path)
    supply_contract = models.ForeignKey(
        SupplyContract, on_delete=models.PROTECT, related_name="file_supply"
    )


class Warehouse(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="warehouse"
    )
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="warehouse")
    remaining = models.DecimalField(default=0, max_digits=7, decimal_places=2)
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


class RemainingProduct(Timestampable, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="remaining_product"
    )
    remaining = models.DecimalField(default=1, max_digits=7, decimal_places=2)


class TechCard(Timestampable, models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(default=1, max_digits=7, decimal_places=2)
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
    quantity = models.DecimalField(max_digits=7, decimal_places=2)


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
