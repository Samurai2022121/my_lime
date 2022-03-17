from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Personnel


class PersonnelFilter(filters.FilterSet):
    s = filters.CharFilter(
        method="search",
        label="поиск по телефону, имени, фамилии",
    )
    is_archived = filters.BooleanFilter(
        method="show_archived",
        label="Показать архивные карточки",
    )

    class Meta:
        model = Personnel
        fields = ("s", "is_archived")

    def search(self, qs, name, value):
        return qs.filter(
            Q(phone_number__icontains=value)
            | Q(local_passports__first_name__icontains=value)
            | Q(local_passports__patronymic__icontains=value)
            | Q(local_passports__last_name__icontains=value)
            | Q(user__phone_number__icontains=value)
            | Q(user__first_name__icontains=value)
            | Q(user__fathers_name__icontains=value)
            | Q(user__last_name__icontains=value)
        )

    def show_archived(self, qs, name, value):
        if value:
            qs |= Q(status=Personnel.WORK_STATUS.archived)
        return qs
