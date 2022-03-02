# Generated by Django 4.0.1 on 2022-02-24 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0024_primarydocument_inheritors"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productiondocument",
            name="primary_document",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                related_name="production_document",
                serialize=False,
                to="internal_api.primarydocument",
            ),
        ),
    ]
