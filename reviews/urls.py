from django.urls import path
from .views import (
    StarGenericAPIView,
    StarredObjectsListAPIView
)


urlpatterns = [
    path('star/', StarGenericAPIView.as_view(), name="star-generic-view"),
    path('starred/', StarredObjectsListAPIView.as_view(), name="starred-list-view"),
]
