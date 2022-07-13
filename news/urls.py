from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    NewsAdminViewset,
    NewsParagraphsImagesViewset,
    NewsParagraphsViewset,
    NewsViewset,
    SectionViewset,
)

router = routers.SimpleRouter()
router.register("news", NewsViewset)
router.register("sections", SectionViewset)
router.register("news-paragraphs", NewsParagraphsViewset)
router.register("news-paragraphs-images", NewsParagraphsImagesViewset)

news_router = NestedSimpleRouter(router, "news", lookup="author")
news_router.register("admin_news", NewsAdminViewset)

urlpatterns = []

urlpatterns += router.urls
urlpatterns += news_router.urls
