import django_filters
from django.db.models import Q

from .models import News


class NewsFilter(django_filters.FilterSet):
    section = django_filters.CharFilter(field_name="section__id", lookup_expr="iexact")
    s = django_filters.CharFilter(
        method="search",
        label="поиск по автору, заголовку",
    )

    class Meta:
        model = News
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(
            Q(author__name__icontains=value)
            | Q(author__surname__icontains=value)
            | Q(headline__icontains=value)
        )
