import django_filters
from django.db.models import Q
from .models import Order


class OrderFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по статусу",
    )

    class Meta:
        model = Order
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(payment_status__icontains=value)
        )
