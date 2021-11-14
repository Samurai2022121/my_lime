from django.contrib.contenttypes.models import ContentType

from rest_framework.views import APIView, Response
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from utils.serializers_utils import CONTENT_TYPES as content_types
from products.models import Product
from products.serializers import ProductSerializer
from recipes.models import Recipe
from recipes.serializers import RecipeSerializer
from .serializers import FavouriteSerializer, StarSerializer
from .models import Favourite, Star


class FavouriteGenericAPIView(CreateAPIView, DestroyAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FavouriteSerializer
    queryset = Favourite.objects.all()

    def delete(self, request, *args, **kwargs):
        content = content_types[request.query_params["content_type"]].objects.get(id=request.query_params["id"])
        Favourite.objects.delete_instance(content, request.user)
        return Response(data=dict(success=True))


class FavouriteObjectsListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        favourites = Favourite.objects.filter(user=user)
        content_type_request_to_content_type_data = {
            'PD': ('product', 'product'),
            'RP': ('recipe', 'recipe')
        }
        if request.query_params.get('content_type', None) in content_type_request_to_content_type_data:
            content_type_app_label, content_type_model =\
                content_type_request_to_content_type_data[request.query_params.get('content_type', None)]

            favourites = favourites.filter(
                content_type=ContentType.objects.filter(
                    app_label=content_type_app_label, model=content_type_model
                ).first()
            )

        favourite_objects = [favourite.content_object for favourite in favourites.order_by('-created_at')]

        model_class_with_model_serializer = (
            (Product, ProductSerializer, 'PD'),
            (Recipe, RecipeSerializer, 'RP')
        )
        data = []
        for favourite_object in favourite_objects:
            for clas, serializer, content_type_response in model_class_with_model_serializer:
                if isinstance(favourite_object, clas):
                    obj_data = serializer(favourite_object, context={'request': request}).data
                    obj_data['content_type'] = content_type_response
                    data.append(obj_data)
                    break

        return Response(data, status=200)


class StarGenericAPIView(CreateAPIView, DestroyAPIView):
    permission_classes = (AllowAny,)
    serializer_class = StarSerializer
    queryset = Star.objects.all()

    def delete(self, request, *args, **kwargs):
        content = content_types[request.query_params["content_type"]].objects.get(id=request.query_params["id"])
        Star.objects.delete_instance(content, request.user)
        return Response(data=dict(success=True))


class StarObjectsListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        stars = Star.objects.filter(user=user)
        content_type_request_to_content_type_data = {
            'PD': ('product', 'product'),
            'RP': ('recipe', 'recipe')
        }
        if request.query_params.get('content_type', None) in content_type_request_to_content_type_data:
            content_type_app_label, content_type_model =\
                content_type_request_to_content_type_data[request.query_params.get('content_type', None)]

            stars = stars.filter(
                content_type=ContentType.objects.filter(
                    app_label=content_type_app_label, model=content_type_model
                ).first()
            )

        stars_objects = [star.content_object for star in stars.order_by('-created_at')]

        model_class_with_model_serializer = (
            (Product, ProductSerializer, 'PD'),
            (Recipe, RecipeSerializer, 'RP')
        )
        data = []
        for star_object in stars_objects:
            for clas, serializer, content_type_response in model_class_with_model_serializer:
                if isinstance(star_object, clas):
                    obj_data = serializer(star_object, context={'request': request}).data
                    obj_data['content_type'] = content_type_response
                    data.append(obj_data)
                    break

        return Response(data, status=200)
