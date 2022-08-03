from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/analytics/(?P<room_name>\w+)/$", consumers.AnalyticsConsumer.as_asgi()
    ),
    path("ws/cashiers/", consumers.AnalyticsCashiersConsumer.as_asgi()),
    path("ws/write-off/", consumers.WriteOffConsumer.as_asgi()),
]
