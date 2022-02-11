from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
)

from .filters import NewsFilter
from .models import News, NewsParagraphs, NewsParagraphsImages, Section
from .serializers import (
    NewsAdminSerializer,
    NewsParagraphsImagesSerializer,
    NewsParagraphsSerializer,
    NewsSerializer,
    SectionSerializer,
)


class NewsAdminViewset(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NewsFilter
    permission_classes = (AllowAny,)
    serializer_class = NewsAdminSerializer
    lookup_field = "id"
    queryset = News.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        return qs


class NewsViewset(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = NewsFilter
    permission_classes = (AllowAny,)
    serializer_class = NewsSerializer
    lookup_field = "id"
    queryset = News.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        return qs


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
