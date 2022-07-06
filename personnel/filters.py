import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from haystack.inputs import Clean
from haystack.query import SearchQuerySet

from .models import Personnel


class FullTextFilter(django_filters.CharFilter):
    QUERY_MIN_LENGTH = 2

    def get_search_queryset(self, queryset):
        return SearchQuerySet().models(queryset.model)

    def filter(self, qs, value):
        if len(value) >= FullTextFilter.QUERY_MIN_LENGTH:
            sqs = self.get_search_queryset(qs)
            for term in value.split():
                sqs = sqs.filter(content=Clean(term))
            qs = qs.filter(pk__in=sqs.values_list("pk", flat=True))
        return qs


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
