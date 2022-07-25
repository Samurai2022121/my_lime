import json
import threading
import time
from io import StringIO

from channels.generic.websocket import WebsocketConsumer

from internal_api.filters import AnaliticsFilter
from internal_api.models.primary_documents import SaleDocument
from internal_api.serializers.analytics import SaleDocumentSerializer


def thread_function(socker, sale_documents, query, interval):
    while True:
        socker.send(
            text_data=json.dumps(
                {
                    "message": SaleDocumentSerializer(
                        sale_documents, many=True, query=query
                    ).data
                }
            )
        )
        time.sleep(interval)


class AnalyticsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close(close_code)

    def receive(self, text_data):
        str_io = StringIO(text_data)
        query_params = json.load(str_io)
        filter_params = query_params.get("filters")
        query = query_params.get("query")
        sale_documents = AnaliticsFilter(
            data=filter_params, queryset=SaleDocument.objects
        ).qs
        interval = int(query_params.get("interval"))

        x = threading.Thread(
            target=thread_function,
            name="228",
            args=(self, sale_documents, query, interval),
        )
        x.start()
