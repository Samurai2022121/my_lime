# Generated by Django 3.2.4 on 2021-12-08 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0017_auto_20211208_0153"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
