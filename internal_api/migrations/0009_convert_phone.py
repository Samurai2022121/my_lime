# Generated by Django 4.0.1 on 2022-03-23 02:00

from django.db import migrations


def convert_phone(apps, schema_editor):
    Supplier = apps.get_model("internal_api", "Supplier")
    for supplier in Supplier.objects.iterator():
        supplier.phone_numbers.append(supplier.phone)
        supplier.save()


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0008_supplier_payment_deferral_supplier_phone_numbers"),
    ]

    operations = [
        migrations.RunPython(convert_phone, reverse_code=lambda: None),
    ]