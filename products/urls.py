from rest_framework import routers

from .views import CategoryViewset, ProductAdminViewset, ProductViewset

router = routers.SimpleRouter()
router.register("products", ProductViewset)
router.register("categories", CategoryViewset)
router.register("admin-products", ProductAdminViewset)

urlpatterns = router.urls
