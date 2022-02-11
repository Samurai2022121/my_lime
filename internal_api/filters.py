import django_filters
from django.db.models import Q
from .models import (
    Supplier,
    Personnel,
    TechCard,
    WarehouseOrder,
)


class SupplierFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по имени, емейлу и телефону",
    )

    class Meta:
        model = Supplier
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
        model = Personnel
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
        model = TechCard
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value)
        )


class WarehouseOrderFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по номеру ордера",
    )

    class Meta:
        model = WarehouseOrder
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(Q(order_number__icontains=value))
