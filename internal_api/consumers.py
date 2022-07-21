import json
import time
from io import StringIO

from channels.generic.websocket import WebsocketConsumer

from internal_api.filters import AnaliticsFilter
from internal_api.models.primary_documents import SaleDocument
from internal_api.serializers.analytics import SaleDocumentSerializer


class AnalyticsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        str_io = StringIO(text_data)
        query_params = json.load(str_io)
        filter_params = query_params.get("filters")
        query = query_params.get("query")
        sale_documents = AnaliticsFilter(
            data=filter_params, queryset=SaleDocument.objects
        ).qs

        while True:
            self.send(
                text_data=json.dumps(
                    {
                        "message": SaleDocumentSerializer(
                            sale_documents, many=True, query=query
                        ).data
                    }
                )
            )
            time.sleep(15)
