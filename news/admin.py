from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import News, Section


@admin.register(Section)
class SectionAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(News)
class NewsAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass
