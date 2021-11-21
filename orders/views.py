from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .serializers import OrdersSerializer
from .models import Order


class OrderViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = OrdersSerializer
    lookup_field = 'id'
    queryset = Order.objects.all()

    def get_object(self):
        return self.queryset.get(id=self.kwargs['id'])

    def get_queryset(self):
        qs = self.queryset
        # if 's' in self.request.query_params:
        #     search_value = self.request.query_params['s']
        #     qs = qs.filter(Q(users__icontains=search_value) | Q(barcode__icontains=search_value))
        return qs
