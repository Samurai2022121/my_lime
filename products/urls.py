from django.urls import path
from rest_framework import routers

from .views import (CategoryViewset, EditProductImagesViewset,
                    ProductMatrixViewset, ProductViewset)

router = routers.SimpleRouter()
router.register("products", ProductViewset)
router.register("categories", CategoryViewset)
router.register("product-images", EditProductImagesViewset)

urlpatterns = [
    path("matrix-products/", ProductMatrixViewset.as_view(), name="matrix-products"),
]

urlpatterns += router.urls
