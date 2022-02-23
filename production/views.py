from django_filters import rest_framework as filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from utils.views_utils import BulkChangeArchiveStatusViewSetMixin

from .filters import DailyMenuPlanLayoutFilter, TechCardFilter
from .models import DailyMenuPlan, TechCard
from .serializers import (
    DailyMenuLayoutSerializer,
    DailyMenuSerializer,
    TechCardSerializer,
)


class TechCardViewSet(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = TechCardSerializer
    lookup_field = "id"
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TechCardFilter
    queryset = TechCard.objects.all()

    def get_queryset(self):
        qs = self.queryset
        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)
        return qs.order_by("name")


class DailyMenuViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = DailyMenuSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    lookup_field = "id"
    queryset = DailyMenuPlan.objects.all()

    @property
    def filterset_class(self):
        if self.action == "layout":
            return DailyMenuPlanLayoutFilter

    @action(methods=["get"], detail=True)
    @swagger_auto_schema(
        responses={200: DailyMenuLayoutSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "shortage",
                description="показывать нехватку ингредиентов",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
            )
        ],
    )
    def layout(self, request, **kwargs):
        menu_id = kwargs.get("id", None)
        qs = DailyMenuPlan.layout.filter(id=menu_id).order_by(
            "dishes__tech_products__product_unit__product__name"
        )
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = DailyMenuLayoutSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DailyMenuLayoutSerializer(qs, many=True)
        return Response(serializer.data)
