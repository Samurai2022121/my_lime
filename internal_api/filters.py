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
            | Q(phone__icontains=value)
        )


class PersonnelFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по телефону, имени, фамилии",
    )

    class Meta:
        model = models.Personnel
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(phone_number__icontains=value)
            | Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
        )


class TechCardFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по имени",
    )

    class Meta:
        model = models.TechCard
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(Q(name__icontains=value))


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
        label="поиск по наименованию продукта, штрихкоду проудукта, id продукта",
    )

    class Meta:
        model = models.Warehouse
        fields = {"product__is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(product__name__icontains=value)
            | Q(product__barcode__icontains=value)
            | Q(product__id__icontains=value)
        )
