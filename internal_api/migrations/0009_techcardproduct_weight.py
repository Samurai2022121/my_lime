# Generated by Django 3.2.4 on 2022-01-24 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0008_auto_20220125_0040"),
    ]

    operations = [
        migrations.AddField(
            model_name="techcardproduct",
            name="weight",
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]