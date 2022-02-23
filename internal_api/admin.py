from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from . import models


@admin.register(models.Shop)
class ShopAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.Personnel)
class PersonnelAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.PrimaryDocument)
class PrimaryDocumentAdmin(
    ListDisplayAllModelFieldsAdminMixin,
    admin.ModelAdmin,
):
    pass


class WarehouseRecordInline(admin.TabularInline):
    model = models.WarehouseRecord
    extra = 1


@admin.register(models.Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        "product_unit",
        "shop",
        "remaining",
        "min_remaining",
        "max_remaining",
        "auto_order",
        "supplier",
        "margin",
    ]
    inlines = [WarehouseRecordInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # TODO: implement this as a custom queryset method
        return qs.annotate(
            remaining=Coalesce(
                Sum("warehouse_records__quantity"),
                Decimal(0),
                output_field=DecimalField(
                    max_digits=7,
                    decimal_places=2,
                ),
            )
        )

    def remaining(self, obj):
        return obj.remaining

    remaining.short_description = "остаток"


@admin.register(models.WarehouseOrder)
class WarehouseOrderAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.WarehouseOrderPositions)
class WarehouseOrderPositionsAdmin(
    ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin
):
    pass


@admin.register(models.Supplier)
class SupplierAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.SupplyContract)
class SupplyContractAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.LegalEntities)
class LegalEntityAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass
