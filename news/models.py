from django.db import models

from users.models import User
from utils.models_utils import Timestampable


class Section(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Новостной раздел")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "новостной раздел"
        verbose_name_plural = "новостные разделы"

    def __str__(self):
        return self.name


class News(Timestampable, models.Model):
    headline = models.CharField(max_length=255, unique=True, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    section = models.ForeignKey(
        Section,
        related_name="news",
        on_delete=models.CASCADE,
        verbose_name="Новостной раздел",
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Автор"
    )
    image = models.ImageField(
        null=True, blank=True, verbose_name="Изображение", upload_to="news/"
    )
    is_archive = models.BooleanField(default=False)

    class Meta:
        verbose_name = "новость"
        verbose_name_plural = "новости"

    def __str__(self):
        return self.headline
