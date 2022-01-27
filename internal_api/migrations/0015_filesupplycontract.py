# Generated by Django 3.2.4 on 2022-01-27 06:39

from django.db import migrations, models
import django.db.models.deletion
import internal_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('internal_api', '0014_remove_supplycontract_contract'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSupplyContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract', models.FileField(upload_to=internal_api.models.create_contract_download_path)),
                ('supply_contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='file_supply', to='internal_api.supplycontract')),
            ],
        ),
    ]
