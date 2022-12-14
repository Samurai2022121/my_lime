from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import Article, ArticleParagraph, ArticleParagraphImage, Section


@admin.register(Section)
class SectionAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ArticleParagraph)
class ArticleParagraphAdmin(ListDisplayAllModelFieldsAdminMixin, OrderedModelAdmin):
    pass


@admin.register(ArticleParagraphImage)
class ArticleParagraphImageAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass
