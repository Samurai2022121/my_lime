from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from utils.views_utils import (BulkChangeArchiveStatusViewSetMixin,
                               BulkUpdateViewSetMixin,
                               OrderingModelViewsetMixin)

from .models import Recipe, RecipeCategory
from .serializers import (RecipeCategorySerializer, RecipeListSerializer,
                          RecipeSerializer)


class RecipeViewset(
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer
    serializer_action_classes = {
        "list": RecipeListSerializer,
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


class RecipeCategoryViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = RecipeCategorySerializer
    lookup_field = "id"
    queryset = RecipeCategory.objects.all()
