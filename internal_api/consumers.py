import json
import threading
import time
from io import StringIO

from channels.generic.websocket import WebsocketConsumer

from internal_api.filters import AnaliticsFilter, WriteOffDocumentFilter
from internal_api.models.primary_documents import SaleDocument, WriteOffDocument
from internal_api.serializers.analytics import (
    CashiersSerializer,
    PopularitySerializer,
    SaleDocumentSerializer,
)


def send_analytics_function(socker, sale_documents, query, interval):
    while True:
        socker.send(
            text_data=json.dumps(
                {
                    "analytics": {
                        "sales": SaleDocumentSerializer(
                            sale_documents, many=True, query=query
                        ).data,
                        "popularity": PopularitySerializer(sale_documents).data,
                    }
                }
            )
        )
        time.sleep(interval)


def send_cashiers_function(socker, sale_documents, query, interval):
    while True:
        socker.send(
            text_data=json.dumps(
                {"cashiers": CashiersSerializer(sale_documents, many=True).data}
            )
        )
        time.sleep(interval)


def send_write_offs(socker, write_off_value, interval):
    while True:
        socker.send(text_data=json.dumps({"write_off_value": write_off_value}))
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
            target=send_analytics_function,
            name="228",
            args=(self, sale_documents, query, interval),
        )
        x.start()


class AnalyticsCashiersConsumer(WebsocketConsumer):
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
            target=send_cashiers_function,
            name="cashiers",
            args=(self, sale_documents, query, interval),
        )
        x.start()


class WriteOffConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close(close_code)

    def receive(self, text_data):
        str_io = StringIO(text_data)
        query_params = json.load(str_io)
        filter_params = query_params.get("filters")
        write_off_documents = WriteOffDocumentFilter(
            data=filter_params, queryset=WriteOffDocument.objects
        ).qs
        interval = int(query_params.get("interval"))
        write_off_value = sum(
            [
                sum(
                    [
                        (record.quantity * record.cost)
                        for record in write_off_document.warehouse_records.all()
                    ]
                )
                for write_off_document in write_off_documents
            ]
        )
        x = threading.Thread(
            target=send_write_offs,
            name="write_off",
            args=(self, str(write_off_value), interval),
        )
        x.start()
