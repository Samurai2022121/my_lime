from rest_framework import routers

from .views import OrderViewset

router = routers.SimpleRouter()
router.register("orders", OrderViewset)

urlpatterns = router.urls
