from collections import defaultdict

from django.db import migrations
from loguru import logger


def remove_duplicates(apps, schema_editor):
    """Make warehouses unique in respect to (shop, product_unit) field tuple."""
    Warehouse = apps.get_model("internal_api", "Warehouse")
    warehouse_qs = Warehouse.objects.prefetch_related("warehouse_records").order_by(
        "pk"
    )
    warehouse_dict = defaultdict(list)
    for warehouse in warehouse_qs:
        warehouse_dict[warehouse.shop_id, warehouse.product_unit_id].append(warehouse)
    for dupe_list in warehouse_dict.values():
        original = dupe_list[0]
        for dupe in dupe_list[1:]:
            logger.info(
                f"Converting {dupe.warehouse_records.count()} records"
                f" of {dupe} to {original}..."
            )
            dupe.warehouse_records.update(warehouse_id=original.pk)
            logger.info(f"Deleting {dupe}...")
            dupe.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0020_alter_warehouseorderpositions_flaw_and_more"),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, reverse_code=lambda x, y: None)
    ]
