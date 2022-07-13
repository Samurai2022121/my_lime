import json

from channels.generic.websocket import WebsocketConsumer

from internal_api.models.shops import Shop
from internal_api.serializers.analytics import ShopSerializer

from .models import WarehouseRecord


class AnalyticsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        shops = Shop.objects.all()

        self.send(
            text_data=json.dumps(
                {"message": [ShopSerializer(shop).data for shop in shops]}
            )
        )
