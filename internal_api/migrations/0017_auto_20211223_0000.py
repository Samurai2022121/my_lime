# Generated by Django 3.2.4 on 2021-12-22 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0016_auto_20211222_0301"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="warehouseorderpositions",
            name="waybill",
        ),
        migrations.AddField(
            model_name="warehouseorder",
            name="waybill",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="warehouseorder",
            name="status",
            field=models.CharField(
                choices=[
                    ("approving", "Подтверждение"),
                    ("delivered", "Уволен"),
                    ("canceled", "Отпуск"),
                    ("dispatched", "Декрет"),
                ],
                max_length=255,
            ),
        ),
    ]
