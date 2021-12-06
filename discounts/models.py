import uuid

from django.db import models

from users.models import User


class LoyaltyDiscount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="loyalty_discount",
        verbose_name="Скидка клиента",
    )
    discount = models.FloatField()

    class Meta:
        verbose_name = "Программа лояльности"
        verbose_name_plural = "Программа лояльности"
