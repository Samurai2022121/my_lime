import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from utils.permissions import ReadOnlyPermissions
from utils.views_utils import (BulkChangeArchiveStatusViewSetMixin,
                               BulkUpdateViewSetMixin)

from .models import News, Section
from .serializers import NewsSerializer, SectionSerializer


class NewsFilter(django_filters.FilterSet):
    section = django_filters.CharFilter(field_name="section__id", lookup_expr="iexact")

    class Meta:
        model = News
        fields = {}


class NewsViewset(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NewsFilter
    permission_classes = (ReadOnlyPermissions,)
    serializer_class = NewsSerializer
    lookup_field = "id"
    queryset = News.objects.all()


class SectionViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = SectionSerializer
    lookup_field = "id"
    queryset = Section.objects.all()
