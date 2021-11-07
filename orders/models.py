from django.db import models

from products.models import Product
from users.models import User


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order', verbose_name='Покупатель')
    products = models.ManyToManyField(Product, verbose_name='Покупки')
    payment_status = models.CharField(max_length=75)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.pk
