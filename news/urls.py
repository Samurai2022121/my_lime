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

news_router = NestedSimpleRouter(router, "news", lookup="author")
news_router.register("admin_news", NewsAdminViewset)


news_paragraphs_router = NestedSimpleRouter(router, "news", lookup="article")
news_paragraphs_router.register(
    "news-paragraphs",
    NewsParagraphsViewset,
)

news_images_router = NestedSimpleRouter(
    news_paragraphs_router, "news-paragraphs", lookup="paragraph"
)
news_images_router.register(
    "images",
    NewsParagraphsImagesViewset,
)

urlpatterns = []

urlpatterns += router.urls
urlpatterns += news_router.urls
urlpatterns += news_paragraphs_router.urls
urlpatterns += news_images_router.urls
