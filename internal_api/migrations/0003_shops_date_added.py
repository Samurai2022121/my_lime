# Generated by Django 3.2.4 on 2021-12-06 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internal_api", "0002_auto_20211122_0210"),
    ]

    operations = [
        migrations.AddField(
            model_name="shops",
            name="date_added",
            field=models.DateTimeField(auto_now=True),
        ),
    ]