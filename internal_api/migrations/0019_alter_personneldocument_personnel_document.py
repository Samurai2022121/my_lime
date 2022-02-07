# Generated by Django 4.0.1 on 2022-02-04 12:52

from django.db import migrations, models
import internal_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('internal_api', '0018_personneldocument_supplycontract_contract_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personneldocument',
            name='personnel_document',
            field=models.FileField(null=True, upload_to=internal_api.models.create_personnel_document_download_path),
        ),
    ]
