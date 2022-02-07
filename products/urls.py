from rest_framework import routers

from .views import CategoryViewset, ProductViewset

router = routers.SimpleRouter()
router.register("products", ProductViewset)
router.register("categories", CategoryViewset)

urlpatterns = router.urls
