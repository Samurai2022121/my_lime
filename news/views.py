import django_filters
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from utils.permissions import ReadOnlyPermissions
from utils.views_utils import (BulkChangeArchiveStatusViewSetMixin,
                               BulkUpdateViewSetMixin)

from .models import (
    News,
    Section,
    NewsParagraphs,
    NewsParagraphsImages,
)
from .serializers import(
    NewsSerializer,
    SectionSerializer,
    NewsParagraphsSerializer,
    NewsParagraphsImagesSerializer,
)


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


class NewsViewset(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NewsFilter
    # permission_classes = (ReadOnlyPermissions,)
    permission_classes = (AllowAny,)
    serializer_class = NewsSerializer
    lookup_field = "id"
    queryset = News.objects.all()


class SectionViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = SectionSerializer
    lookup_field = "id"
    queryset = Section.objects.all()


class NewsParagraphsViewset(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    permission_classes = (AllowAny,)
    lookup_field = "id"
    serializer_class = NewsParagraphsSerializer
    queryset = NewsParagraphs.objects.all()


class NewsParagraphsImagesViewset(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    permission_classes = (AllowAny,)
    lookup_field = "id"
    serializer_class = NewsParagraphsImagesSerializer
    queryset = NewsParagraphsImages.objects.all()
