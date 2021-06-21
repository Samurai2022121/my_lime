from django.urls import path
from rest_framework import routers

from products.views import (
    ProductViewset,
)

router = routers.SimpleRouter()
router.register('products', ProductViewset)

urlpatterns = []

urlpatterns += router.urls
