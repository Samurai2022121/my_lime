from django.urls import path
from .views import (
    FavouriteGenericAPIView,
    FavouriteObjectsListAPIView
)


urlpatterns = [
    path('favourite/', FavouriteGenericAPIView.as_view(), name="favourite-generic-view"),
    path('favourite-list/', FavouriteObjectsListAPIView.as_view(), name="favourite-list-view"),
]
