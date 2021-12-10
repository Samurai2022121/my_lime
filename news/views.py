import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission

from utils.views_utils import ProductPagination

from .models import News, Section
from .serializers import NewsSerializer, SectionSerializer


class ReadOnlyPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user and request.user.is_authenticated


class NewsFilter(django_filters.FilterSet):
    section = django_filters.CharFilter(field_name="section__id", lookup_expr="iexact")

    class Meta:
        model = News
        fields = {}


class NewsViewset(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    pagination_class = ProductPagination
    filterset_class = NewsFilter
    permission_classes = (ReadOnlyPermissions,)
    serializer_class = NewsSerializer
    lookup_field = "id"
    queryset = News.objects.all()


class SectionViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SectionSerializer
    lookup_field = "id"
    queryset = Section.objects.all()
