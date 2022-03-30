from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0035_alter_category_name_alter_category_unique_together"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product", old_name="vat_value", new_name="vat_rate"
        ),
        migrations.AlterField(
            model_name="product",
            name="vat_rate",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=7,
                null=True,
                verbose_name="Ставка НДС, %",
            ),
        ),
    ]
