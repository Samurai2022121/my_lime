from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('shop/', include(('products.urls', 'products'), namespace='products')),
    path('cookbook/', include(('recipes.urls', 'recipes'), namespace='recipes')),
    path('rating/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('news/', include(('news.urls', 'news'), namespace='news')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
