import django_filters
from django.db.models import Q
from .models import User, CustomerDeliveryAddress


class UserFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по номеру телефона, имени, фамилии, id",
    )

    class Meta:
        model = User
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(phone_number__icontains=value)
            | Q(name__icontains=value)
            | Q(surname__icontains=value)
            | Q(id__icontains=value)
        )


class CustomerDeliveryAddressFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по имени, фамилии, номеру телефона, емейлу",
    )

    class Meta:
        model = CustomerDeliveryAddress
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value)
            | Q(surname__icontains=value)
            | Q(phone_number__icontains=value)
            | Q(email__icontains=value)
        )
