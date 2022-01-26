# Generated by Django 3.2.4 on 2022-01-26 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0010_auto_20220126_1517"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menudish",
            name="dish",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="internal_api.techcard"
            ),
        ),
        migrations.AlterField(
            model_name="menudish",
            name="menu",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="menu_dish",
                to="internal_api.dailymenuplan",
            ),
        ),
    ]
