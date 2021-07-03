from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Recipe, RecipeCategory
from .serializers import RecipeSerializer, RecipeListSerializer, RecipeCategorySerializer
from utils.views_utils import ProductPagination


class RecipeViewset(viewsets.ModelViewSet):
    pagination_class = ProductPagination
    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer
    serializer_action_classes = {
        'list': RecipeListSerializer
    }
    lookup_field = 'id'
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, super().get_serializer_class())

    def get_object(self):
        return self.queryset.get(id=self.kwargs['id'])

    def get_queryset(self):
        return self.queryset.order_by(
            'publication_date'
        )


class RecipeCategoryViewset(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = RecipeCategorySerializer
    lookup_field = 'id'
    queryset = RecipeCategory.objects.all()
