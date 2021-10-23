# Generated by Django 3.2.4 on 2021-10-23 20:56

from django.db import migrations, models
import utils.models_utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_generatedpassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generatedpassword',
            name='password',
            field=models.CharField(default=utils.models_utils.generate_new_password, editable=False, max_length=8),
        ),
    ]
