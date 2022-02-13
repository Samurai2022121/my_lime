from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from utils.views_utils import (
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    OrderingModelViewsetMixin,
)

from .filters import RecipeFilter
from .models import Recipe, RecipeCategory
from .serializers import (
    RecipeAdminSerializer,
    RecipeCategorySerializer,
    RecipeListAdminSerializer,
    RecipeListSerializer,
    RecipeSerializer,
)


class RecipeViewset(
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
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
        qs = self.queryset

        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)

        ordering_fields = self.get_ordering_fields()
        if ordering_fields:
            qs = qs.order_by(*ordering_fields)
        else:
            qs = qs.order_by("name")

        return qs


class RecipeAdminViewset(
    BulkChangeArchiveStatusViewSetMixin,
    BulkUpdateViewSetMixin,
    OrderingModelViewsetMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (AllowAny,)
    serializer_class = RecipeAdminSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_action_classes = {
        "list": RecipeListAdminSerializer,
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
        qs = self.queryset
        ordering_fields = self.get_ordering_fields()

        if "is_archive" not in self.request.query_params:
            qs = qs.filter(is_archive=False)

        if ordering_fields:
            qs = qs.order_by(*ordering_fields)
        else:
            qs = qs.order_by("name")

        return qs


class RecipeCategoryViewset(BulkChangeArchiveStatusViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    serializer_class = RecipeCategorySerializer
    lookup_field = "id"
    queryset = RecipeCategory.objects.all()
