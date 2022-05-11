from django.db import migrations


def fill_batches(apps, schema_editor):
    WarehouseRecord = apps.get_model("internal_api", "WarehouseRecord")
    Batch = apps.get_model("internal_api", "Batch")

    for whr in WarehouseRecord.objects.iterator():
        if whr.warehouse.supplier:
            whr.batch, _ = (
                Batch.objects.filter(
                    warehouse_records__warehouse_id=whr.warehouse_id,
                )
                .distinct()
                .get_or_create(
                    supplier=whr.warehouse.supplier,
                )
            )
            whr.save()


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0016_batch_warehouserecord_batch"),
    ]

    operations = [
        migrations.RunPython(fill_batches, reverse_code=lambda x, y: None),
    ]
