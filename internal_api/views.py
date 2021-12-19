from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED

from . import models, serializers


class ShopViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ShopSerializer
    lookup_field = "id"
    queryset = models.Shop.objects.all()


class PersonnelViewSet(viewsets.ModelViewSet):
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
