from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from utils.views_utils import ProductPagination

from .models import News, Section
from .serializers import NewsSerializer, SectionSerializer


class NewsViewset(viewsets.ModelViewSet):
    pagination_class = ProductPagination
    permission_classes = (AllowAny,)
    serializer_class = NewsSerializer
    lookup_field = "id"
    queryset = News.objects.all()


class SectionViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SectionSerializer
    lookup_field = "id"
    queryset = Section.objects.all()
