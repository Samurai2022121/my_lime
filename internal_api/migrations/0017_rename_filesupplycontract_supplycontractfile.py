# Generated by Django 3.2.4 on 2022-01-27 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('internal_api', '0016_auto_20220127_1522'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FileSupplyContract',
            new_name='SupplyContractFile',
        ),
    ]
