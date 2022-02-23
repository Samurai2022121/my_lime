from rest_framework import routers

from .views import DailyMenuViewSet, TechCardViewSet

router = routers.SimpleRouter()
router.register("tech-card", TechCardViewSet)
router.register("daily-menu", DailyMenuViewSet)

urlpatterns = router.urls
