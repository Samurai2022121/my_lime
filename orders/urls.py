from django.urls import include, path
from rest_framework import routers

from .views import OrderViewset

router = routers.SimpleRouter()
router.register("orders", OrderViewset)

urlpatterns = [
    path(r"outlets/<int:shop_id>/", include(router.urls)),
]
