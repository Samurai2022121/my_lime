from django.urls import path
from .views import (
    FavouriteGenericAPIView,
    FavouriteObjectsListAPIView,
    StarGenericAPIView,
    StarObjectsListAPIView
)


urlpatterns = [
    path('favourite/', FavouriteGenericAPIView.as_view(), name="favourite-generic-view"),
    path('favourite-list/', FavouriteObjectsListAPIView.as_view(), name="favourite-list-view"),
    path('stared/', StarGenericAPIView.as_view(), name="stared-generic-view"),
    path('stared-list/', StarObjectsListAPIView.as_view(), name="stared-list-view"),
]
