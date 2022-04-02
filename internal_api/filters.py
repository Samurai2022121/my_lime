import django_filters
from django.db.models import Q

from . import models


class SupplierFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по имени, емейлу и телефону",
    )

    class Meta:
        model = models.Supplier
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value)
            | Q(email__icontains=value)
            | Q(phone_numbers__icontains=value)
        )


class WarehouseOrderFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по номеру заказа",
    )

    class Meta:
        model = models.WarehouseOrder
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(Q(order_number__icontains=value))


class LegalEntityFilterSet(django_filters.FilterSet):

    """Searches through `registration_id` and/or `name` fields."""

    s = django_filters.CharFilter(
        method="search_by_id_or_name",
        label="регистрационный номер или наименование",
    )

    class Meta:
        model = models.LegalEntities
        fields = ("s",)

    def search_by_id_or_name(self, qs, name, value):
        return qs.filter(Q(registration_id__contains=value) | Q(name__icontains=value))


class ShopFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по названию, адресу, id",
    )

    class Meta:
        model = models.Shop
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value)
            | Q(address__icontains=value)
            | Q(id__icontains=value)
        )


class WarehouseFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по наименованию продукта, штрихкоду продукта, id продукта",
    )
    is_archive = django_filters.BooleanFilter(
        field_name="product_unit__product__is_archive",
        label="показывать архивные запасы",
    )
    remaining = django_filters.RangeFilter(
        label="отобрать по количеству на складе",
    )

    class Meta:
        model = models.Warehouse
        fields = ("s",)

    def search(self, qs, name, value):
        return qs.filter(
            Q(product_unit__product__name__icontains=value)
            | Q(product_unit__barcode__icontains=value)
            | Q(product_unit__product__id__icontains=value)
        )


class PrimaryDocumentFilter(django_filters.FilterSet):
    created = django_filters.DateFromToRangeFilter(
        field_name="created_at",
        label="период времени",
    )
    number = django_filters.CharFilter(lookup_expr="icontains", label="номер")

    class Meta:
        model = models.PrimaryDocument
        fields = ("created", "number")
