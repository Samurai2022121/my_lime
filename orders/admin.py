from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import Order


@admin.register(Order)
class OrderAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass
