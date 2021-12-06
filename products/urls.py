from rest_framework import routers

from .views import CategoryViewset, EditProductImagesViewset, ProductViewset

router = routers.SimpleRouter()
router.register("products", ProductViewset)
router.register("categories", CategoryViewset)
router.register("product-images", EditProductImagesViewset)

urlpatterns = router.urls
