import django_filters
from django.db.models import Q

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по наименованию",
    )

    class Meta:
        model = Recipe
        fields = {
            "is_archive": ["exact"],
        }

    def search(self, qs, name, value):
        return qs.filter(Q(name__icontains=value))
