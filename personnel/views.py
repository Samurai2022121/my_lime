from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet
from rest_framework_nested.viewsets import NestedViewSetMixin

from utils import permissions as perms
from utils.serializers_utils import BulkActionSerializer
from utils.views_utils import OrderingModelViewsetMixin

from .filters import PersonnelFilter
from .models import LocalPassport, Personnel, PersonnelDocument, Position
from .serializers import (
    LocalPassportSerializer,
    PersonnelDocumentSerializer,
    PersonnelSerializer,
    PositionSerializer,
)


class PositionViewSet(ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_staff, write=perms.allow_staff),
    )
    serializer_class = PositionSerializer
    lookup_field = "id"
    queryset = Position.objects.order_by("name")


class PersonnelViewSet(ModelViewSet, OrderingModelViewsetMixin):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PersonnelFilter
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_staff, write=perms.allow_staff),
    )
    serializer_class = PersonnelSerializer
    lookup_field = "id"
    queryset = Personnel.objects.exclude(status=Personnel.WORK_STATUS.archived)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = Personnel.WORK_STATUS.archived
        instance.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="bulk-archive")
    def change_archive_status(self, request, **kwargs):
        serialized_data = BulkActionSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        self.queryset.filter(id__in=instances).update(
            status=Personnel.WORK_STATUS.archived,
        )
        return Response(status=HTTP_200_OK)


class PersonnelDocumentViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_staff, write=perms.allow_staff),
    )
    serializer_class = PersonnelDocumentSerializer
    lookup_field = "id"
    parent_lookup_kwargs = {
        "personnel_id": "employee__id",
    }
    queryset = PersonnelDocument.objects.order_by("number")

    def perform_create(self, serializer):
        serializer.save(employee_id=self.kwargs["personnel_id"])


class LocalPassportViewSet(NestedViewSetMixin, ModelViewSet):
    permission_classes = (
        perms.ReadWritePermission(read=perms.allow_staff, write=perms.allow_staff),
    )
    serializer_class = LocalPassportSerializer
    lookup_field = "id"
    parent_lookup_kwargs = {
        "personnel_id": "employee__id",
    }
    queryset = LocalPassport.objects

    def perform_create(self, serializer):
        serializer.save(employee_id=self.kwargs["personnel_id"])
