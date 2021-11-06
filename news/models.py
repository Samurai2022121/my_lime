from django.db import models

from users.models import User


class Section(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Новостной раздел')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'новостной раздел'
        verbose_name_plural = 'новостные разделы'

    def __str__(self):
        return self.name


class News(models.Model):
    headline = models.CharField(max_length=255, unique=True, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    section = models.ForeignKey(Section, related_name='news', on_delete=models.SET_DEFAULT,
                                default='Общее', verbose_name='Новостной раздел')
    publication_date = models.DateTimeField(auto_now=True, verbose_name='Дата публикации')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    image = models.ImageField(null=True, blank=True, verbose_name='Изображение', upload_to="news/")

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'новости'

    def __str__(self):
        return self.headline
