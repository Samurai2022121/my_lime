# Generated by Django 3.2.4 on 2021-11-21 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_order_placed',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(default=1, max_length=75),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('card_pre', 'Debit card before receiving'), ('card_post', 'Debit card on receiving'), ('cash', 'Cash')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]
