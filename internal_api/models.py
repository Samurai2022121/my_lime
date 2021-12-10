from django.core.validators import RegexValidator
from django.db import models

from products.models import Product


class Shop(models.Model):
    address = models.TextField()
    name = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now=True)


class Warehouse(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="warehouse"
    )
    measure_unit = models.CharField(max_length=35)
    remaining = models.FloatField(default=0)
    min_remaining = models.FloatField(default=0)
    max_remaining = models.FloatField(default=0)
    supplier = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r"^\+?\d{9,15}$",
        message='Phone number must be entered in the format: "+999999999". '
        "Up to 15 digits allowed.",
    )
    supplier_phone = models.CharField(
        validators=[phone_regex], max_length=17, unique=True
    )


class RemainingProduct(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="remaining_product"
    )
    remaining = models.FloatField(default=1)


class TechCard(models.Model):
    product = models.ManyToManyField(Product, related_name="tech_card_product")
    amount = models.FloatField(default=1)
