from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Lime API",
        default_version="v1",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="vlad.fedyayev@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("admin/", admin.site.urls),
    path("discounts/", include(("discounts.urls", "discounts"), namespace="discounts")),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("product/", include(("products.urls", "products"), namespace="products")),
    path("cookbook/", include(("recipes.urls", "recipes"), namespace="recipes")),
    path("rating/", include(("reviews.urls", "reviews"), namespace="reviews")),
    path("news/", include(("news.urls", "news"), namespace="news")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path(
        "internal-api/",
        include(("internal_api.urls", "internal_api"), namespace="internal_api"),
    ),
    path(
        "personnel/",
        include(("personnel.urls", "personnel"), namespace="personnel"),
    ),
    path(
        "production/",
        include(("production.urls", "production"), namespace="production"),
    ),
    path("basket/", include(("basket.urls", "basket"), namespace="basket")),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
