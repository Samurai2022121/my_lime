from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from products.models import Product
from utils.serializers_utils import BulkUpdateSerializer
from utils.views_utils import (BulkChangeArchiveStatusViewSetMixin,
                               BulkUpdateViewSetMixin)

from . import models, serializers


class ShopViewSet(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ShopSerializer
    lookup_field = "id"
    queryset = models.Shop.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )


class PersonnelViewSet(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.PersonnelSerializer
    lookup_field = "id"
    queryset = models.Personnel.objects.all()


class WarehouseViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseSerializer
    lookup_field = "id"
    queryset = models.Warehouse.objects.all()

    def get_queryset(self):
        qs = self.queryset
        outlet_id = self.request.query_params.get("outlet", None)
        if outlet_id:
            qs = qs.filter(shop=outlet_id)
        return qs

    @action(detail=False, methods=["post"], url_path="bulk_update")
    def bulk_update(self, request, **kwargs):
        serialized_data = BulkUpdateSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        for instance in instances:
            image_id = instance.pop("id", None)
            product_id = instance.pop("product")
            if not product_id:
                return Response(
                    status=HTTP_400_BAD_REQUEST, data={"message": "Товар не существует"}
                )
            product = Product.objects.get(id=product_id)
            instance.update({"product": product})
            if image_id:
                self.queryset.filter(id=image_id).update(**instance)
            else:
                models.Warehouse.objects.create(**instance)
        return Response(status=HTTP_202_ACCEPTED)


class UploadCSVGenericView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UploadCSVSerializer

    def post(self, request):
        return Response(status=HTTP_202_ACCEPTED)


class WarehouseOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.WarehouseOrderSerializer
    lookup_field = "id"
    queryset = models.WarehouseOrder.objects.all()


class SupplierViewSet(
    BulkChangeArchiveStatusViewSetMixin, BulkUpdateViewSetMixin, viewsets.ModelViewSet
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SupplierSerializer
    lookup_field = "id"
    queryset = models.Supplier.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )
