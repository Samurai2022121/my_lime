from django.db import migrations


def move_prices(apps, schema_editor):
    Warehouse = apps.get_model("internal_api", "Warehouse")

    for warehouse in Warehouse.objects.iterator():
        warehouse.price = warehouse.product_unit.product.price
        warehouse.save()


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0030_productunit_barcode_productunit_for_scales_and_more"),
        ("internal_api", "0004_alter_warehouse_price"),
    ]

    operations = [
        migrations.RunPython(move_prices, reverse_code=lambda x, y: None),
    ]
