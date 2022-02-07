import django_filters
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
)

from .models import News, Section
from .serializers import NewsAdminSerializer, NewsSerializer, SectionSerializer


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


class NewsViewset(viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NewsFilter
    serializer_class = NewsSerializer
    lookup_field = "id"
    queryset = News.objects.all()

    def get_queryset(self):
        qs = self.queryset.filter(is_archive=False)
        return qs.order_by("created_at")


class NewsAdminViewset(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NewsFilter
    serializer_class = NewsAdminSerializer
    lookup_field = "id"
    queryset = News.objects.all()

    def get_queryset(self):
        if "is_archive" not in self.request.query_params:
            self.queryset = self.queryset.filter(is_archive=False)
        return self.queryset.order_by("created_at")


class SectionViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = SectionSerializer
    lookup_field = "id"
    queryset = Section.objects.all()
