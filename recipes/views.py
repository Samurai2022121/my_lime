from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from utils.serializers_utils import BulkUpdateSerializer
from utils.views_utils import (BulkUpdateViewSetMixin,
                               OrderingModelViewsetMixin, ProductPagination)

from .models import Recipe, RecipeCategory
from .serializers import (RecipeCategorySerializer, RecipeListSerializer,
                          RecipeSerializer)


class RecipeViewset(
    BulkUpdateViewSetMixin, OrderingModelViewsetMixin, viewsets.ModelViewSet
):
    pagination_class = ProductPagination
    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer
    serializer_action_classes = {
        "list": RecipeListSerializer,
        "bulk-update": BulkUpdateSerializer,
    }
    lookup_field = "id"
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(
            self.action, super().get_serializer_class()
        )

    def get_object(self):
        return self.queryset.get(id=self.kwargs["id"])

    def get_queryset(self):
        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            return self.queryset.order_by(*ordering_fields)
        return self.queryset


class RecipeCategoryViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RecipeCategorySerializer
    lookup_field = "id"
    queryset = RecipeCategory.objects.all()
