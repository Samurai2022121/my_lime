from pathlib import Path

from django.http import HttpResponse
from django_filters import rest_framework as filters
from docxtpl import DocxTemplate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from utils import permissions as perms
from utils.views_utils import BulkChangeArchiveStatusViewSetMixin

from .filters import DailyMenuPlanLayoutFilter, TechCardFilter
from .models import DailyMenuPlan, TechCard
from .serializers import (
    DailyMenuLayoutSerializer,
    DailyMenuSerializer,
    TechCardSerializer,
)


class TechCardViewSet(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            write=perms.allow_staff,
            change_archive_status=perms.allow_staff,
            render_docx=perms.allow_staff,
        ),
    )
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

    @action(methods=["get"], detail=True, url_path="render-docx")
    def render_docx(self, request, **kwargs):
        tech_card = self.get_object()
        docx = DocxTemplate(
            Path(__file__).parent / "templates" / "production" / "techcard.docx"
        )
        docx.render(context={"obj": tech_card})
        response = HttpResponse(
            content_type=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            )
        )
        docx.save(response)
        return response


class DailyMenuViewSet(viewsets.ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(
            read=perms.allow_staff,
            write=perms.allow_staff,
            layout=perms.allow_staff,
        ),
    )
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
