from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    LocalPassportViewSet,
    PersonnelDocumentViewSet,
    PersonnelViewSet,
    PositionViewSet,
)

router = SimpleRouter()
router.register("personnel", PersonnelViewSet)
router.register("positions", PositionViewSet)

docs_router = NestedSimpleRouter(router, "personnel", lookup="personnel")
docs_router.register("documents", PersonnelDocumentViewSet)

passport_router = NestedSimpleRouter(router, "personnel", lookup="personnel")
passport_router.register("passports", LocalPassportViewSet)

urlpatterns = router.urls
urlpatterns += docs_router.urls
urlpatterns += passport_router.urls
