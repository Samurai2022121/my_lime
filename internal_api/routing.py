from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/analytics/(?P<room_name>\w+)/$", consumers.AnalyticsConsumer.as_asgi()
    ),
]
