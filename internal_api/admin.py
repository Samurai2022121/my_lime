from decimal import Decimal

from django import forms
from django.contrib import admin
from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce
from django.urls import path

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from . import models


@admin.register(models.Shop)
class ShopAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


@admin.register(models.Personnel)
class PersonnelAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


class WarehouseRecordInline(admin.TabularInline):
    model = models.WarehouseRecord
    extra = 1


class PrimaryDocumentSubclassFilter(admin.SimpleListFilter):
    title = "первичный документ"
    parameter_name = "primary_document"

    def lookups(self, request, model_admin):
        return models.PrimaryDocument.SUBCLASS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.exclude(**{self.value(): None})

        return queryset


@admin.register(models.PrimaryDocument)
class PrimaryDocumentAdmin(admin.ModelAdmin):
    """
    Inspired by
    https://schinckel.net/2016/04/30/multi-table-inheritance-and-the-django-admin/
    """

    list_display = ("document_type", "created_at", "number", "author")
    list_filter = (PrimaryDocumentSubclassFilter,)
    inlines = (WarehouseRecordInline,)

    def document_type(self, obj):
        return obj._meta.verbose_name

    document_type.short_description = "вид документа"

    def get_queryset(self, request):
        return super().get_queryset(request).select_subclasses()

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is None:
            Model = models.PrimaryDocument.SUBCLASS(request.GET.get("document_choice"))
        else:
            Model = obj.__class__

        # reload page when primary document subclass changes
        RELOAD_PAGE = "window.location.search='?document_choice=' + this.value"

        # TODO: grab all existing field values, and pass them as query
        #   string values
        class ModelForm(forms.ModelForm):
            if not obj:
                document_choice = forms.ChoiceField(
                    choices=[("", "Выберите...")]
                    + models.PrimaryDocument.SUBCLASS_CHOICES,
                    widget=forms.Select(attrs={"onchange": RELOAD_PAGE}),
                )

            class Meta:
                model = Model
                exclude = ()

        return ModelForm

    def get_fields(self, request, obj=None):
        # `primary_document` should be the first field
        fields = super().get_fields(request, obj)

        if "document_choice" in fields:
            fields.remove("document_choice")
            fields = ["document_choice"] + fields

        return fields

    def get_urls(self):
        # install named urls that match the subclass ones, but bounce
        # to the relevant superclass ones (since they should be able
        # to handle rendering the correct form)
        urls = super().get_urls()
        existing = "{}_{}_".format(
            self.model._meta.app_label,
            self.model._meta.model_name,
        )
        subclass_urls = []
        for _, model in models.PrimaryDocument.SUBCLASS_OBJECT_CHOICES.items():
            opts = model._meta
            replace = "{}_{}_".format(opts.app_label, opts.model_name)
            subclass_urls.extend(
                [
                    path(
                        pattern.pattern._route,
                        pattern.callback,
                        name=pattern.name.replace(existing, replace),
                    )
                    for pattern in urls
                    if pattern.name
                ]
            )

        return urls + subclass_urls


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
    list_filter = ("shop__name", "product_unit__unit__name")

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


class WarehouseOrderPositionsInline(admin.TabularInline):
    model = models.WarehouseOrderPositions
    extra = 1


@admin.register(models.WarehouseOrder)
class WarehouseOrderAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [WarehouseOrderPositionsInline]


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
