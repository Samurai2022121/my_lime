# Generated by Django 3.2.4 on 2021-12-25 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0012_alter_user_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerdeliveryaddress",
            name="is_archive",
            field=models.BooleanField(default=False),
        ),
    ]
