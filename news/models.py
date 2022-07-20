from django.core.validators import FileExtensionValidator
from django.db import models
from ordered_model.models import OrderedModel

from users.models import User
from utils.enums import Permissions
from utils.models_utils import Timestampable


class Section(models.Model):

    name = models.CharField(max_length=50, unique=True, verbose_name="Новостной раздел")
    description = models.TextField(verbose_name="Описание")
    image = models.FileField(
        null=True,
        blank=True,
        verbose_name="Изображение",
        upload_to="news/",
        validators=[FileExtensionValidator(["svg", "png", "jpg"])],
    )
    permission = models.PositiveIntegerField(
        choices=Permissions.choices,
        verbose_name="permission",
        default=Permissions.FOR_ALL,
    )

    class Meta:
        verbose_name = "новостной раздел"
        verbose_name_plural = "новостные разделы"

    def __str__(self):
        return self.name


class Article(Timestampable, models.Model):
    headline = models.CharField(max_length=255, unique=True, verbose_name="Заголовок")
    section = models.ForeignKey(
        Section,
        related_name="news",
        on_delete=models.CASCADE,
        verbose_name="Новостной раздел",
    )
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Автор"
    )

    is_archive = models.BooleanField(default=False)

    class Meta:
        verbose_name = "новость"
        verbose_name_plural = "новости"

    def __str__(self):
        return self.headline


class ArticleParagraph(OrderedModel):
    news = models.ForeignKey(
        Article, related_name="news_paragraphs", on_delete=models.PROTECT
    )
    subheadline = models.CharField(max_length=255, null=True)
    text = models.TextField(verbose_name="Текст")
    order = models.PositiveIntegerField(
        db_index=True, verbose_name="List order", default=0
    )

    order_with_respect_to = "news"

    class Meta:
        ordering = ("order",)
        verbose_name = "Параграф"
        verbose_name_plural = "Параграфы"


class ArticleParagraphImage(models.Model):
    news_paragraphs = models.ForeignKey(
        ArticleParagraph,
        related_name="news_paragraphs_images",
        on_delete=models.PROTECT,
    )
    image = models.ImageField(
        null=True, blank=True, verbose_name="Изображение", upload_to="news/"
    )
