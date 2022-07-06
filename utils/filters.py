import django_filters
from haystack.inputs import Clean
from haystack.query import SearchQuerySet


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
