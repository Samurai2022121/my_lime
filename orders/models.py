from django.db import models

from products.models import Product
from users.models import User


class Order(models.Model):
    PAYMENT_METHODS = (
        ('card_pre', 'Debit card before receiving'),
        ('card_post', 'Debit card on receiving'),
        ('cash', 'Cash'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    products = models.ManyToManyField(Product, verbose_name='Покупки')
    payment_status = models.CharField(max_length=75)
    order_status = models.CharField(max_length=75)
    date_order_placed = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.pk
