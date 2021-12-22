from django.db import models

from products.models import Product
from utils.models_utils import Timestampable, phone_regex


class Shop(models.Model):
    address = models.TextField()
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now=True)


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


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True
    )
    extra_info = models.JSONField(null=True, blank=True)


class Warehouse(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="warehouse"
    )
    shop = models.PositiveIntegerField(db_index=True)
    remaining = models.FloatField(default=0, blank=True, null=True)
    min_remaining = models.FloatField(default=0, blank=True, null=True)
    max_remaining = models.FloatField(default=0, blank=True, null=True)
    supplier = models.CharField(max_length=255, blank=True, null=True)
    margin = models.FloatField(blank=True, null=True)
    supplier_email = models.EmailField(blank=True, null=True)
    supplier_phone = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True
    )
    auto_order = models.BooleanField(default=False)


class RemainingProduct(Timestampable, models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="remaining_product"
    )
    remaining = models.FloatField(default=1)


class TechCard(Timestampable, models.Model):
    name = models.CharField(max_length=255)
    product = models.ManyToManyField(Product, related_name="tech_card_product")
    amount = models.FloatField(default=1)
    author = models.ForeignKey(Personnel, on_delete=models.PROTECT)
    is_archived = models.BooleanField(default=False)


class DailyMenuPlan(Timestampable, models.Model):
    dishes = models.ManyToManyField(TechCard, through="MenuDishes")
    author = models.ForeignKey(Personnel, on_delete=models.PROTECT)


class MenuDishes(models.Model):
    dish = models.ForeignKey(TechCard, on_delete=models.PROTECT)
    menu = models.ForeignKey(DailyMenuPlan, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)


class WarehouseOrder(Timestampable, models.Model):
    ORDER_STATUSES = (
        ("approving", "Подтверждение"),
        ("delivered", "Уволен"),
        ("canceled", "Отпуск"),
        ("dispatched", "Декрет"),
    )

    status = models.CharField(max_length=255, choices=ORDER_STATUSES)
    supplier = models.CharField(max_length=255)
    order_positions = models.ManyToManyField(Product, through="WarehouseOrderPositions")
    waybill = models.CharField(max_length=255, null=True, blank=True)


class WarehouseOrderPositions(models.Model):
    warehouse_order = models.ForeignKey(WarehouseOrder, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.FloatField(default=0)
    bonus = models.IntegerField(default=0)
    special = models.FloatField(default=0)
    flaw = models.FloatField(default=0)
