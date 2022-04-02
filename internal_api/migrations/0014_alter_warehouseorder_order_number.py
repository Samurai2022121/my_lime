# Generated by Django 4.0.1 on 2022-04-02 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0013_returndocument"),
    ]

    operations = [
        migrations.RenameField(
            model_name="warehouseorder",
            old_name="order_number",
            new_name="number",
        ),
        migrations.AlterField(
            model_name="warehouseorder",
            name="number",
            field=models.CharField(
                blank=True,
                max_length=255,
                unique=True,
                verbose_name="номер",
            ),
        ),
    ]
