import django_filters
from django.db.models import Q

from .models import DailyMenuPlan, TechCard


class TechCardFilter(django_filters.FilterSet):
    s = django_filters.CharFilter(
        method="search",
        label="поиск по имени",
    )

    class Meta:
        model = TechCard
        fields = {"is_archive": ["exact"]}

    def search(self, qs, name, value):
        return qs.filter(Q(name__icontains=value))


class DailyMenuPlanLayoutFilter(django_filters.FilterSet):

    shortage = django_filters.BooleanFilter(
        method="display_shortage",
        label="показывать нехватку ингредиентов",
    )

    class Meta:
        model = DailyMenuPlan
        fields = ("shortage",)

    def display_shortage(self, qs, name, value):
        if value:
            return qs.filter(shortage__gt=0)
        else:
            return qs.filter(shortage__lte=0)
