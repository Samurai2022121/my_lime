from django.db.models import Q
from django_filters import rest_framework as filters

from utils.filters import FullTextFilter

from .models import Personnel


class PersonnelFullTextFilter(FullTextFilter):
    def get_search_queryset(self, queryset):
        sqs = super().get_search_queryset(queryset)
        return sqs


class PersonnelFilter(filters.FilterSet):
    s = PersonnelFullTextFilter(
        label="поиск по телефону, имени, фамилии",
    )
    is_archived = filters.BooleanFilter(
        method="show_archived",
        label="Показать архивные карточки",
    )

    class Meta:
        model = Personnel
        fields = ("s", "is_archived")

    def show_archived(self, qs, name, value):
        if value:
            qs |= Q(status=Personnel.WORK_STATUS.archived)
        return qs
