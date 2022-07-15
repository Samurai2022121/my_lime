import io
import json
from io import StringIO

from channels.generic.websocket import WebsocketConsumer
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from internal_api.filters import AnaliticsFilter
from internal_api.models.primary_documents import SaleDocument
from internal_api.serializers.analytics import ProductSerializer


class AnalyticsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        str_io = StringIO(text_data)
        filters = json.load(str_io)
        result = {}
        for sale_document in AnaliticsFilter(
            data=filters.get("message"), queryset=SaleDocument.objects
        ).qs:
            for warehouse_record in sale_document.warehouse_records.all():
                if (
                    result.get(warehouse_record.warehouse.product_unit.product.id)
                    is None
                ):
                    result.update(
                        {
                            warehouse_record.warehouse.product_unit.product.id: {
                                "id": warehouse_record.warehouse.product_unit.product.id,
                                "name": warehouse_record.warehouse.product_unit.product.name,
                                "quantity": [
                                    warehouse_record.quantity,
                                ],
                                "cost": [
                                    warehouse_record.cost,
                                ],
                                "margin": [
                                    warehouse_record.warehouse.margin,
                                ]
                                if warehouse_record.warehouse.margin is not None
                                else [],
                            }
                        }
                    )
                else:
                    record = result.get(
                        warehouse_record.warehouse.product_unit.product.id
                    )
                    record["quantity"].append(warehouse_record.quantity)
                    record["cost"].append(warehouse_record.cost)
                    if warehouse_record.warehouse.margin is not None:
                        record["margin"].append(warehouse_record.warehouse.margin)
                    result.update(
                        {warehouse_record.warehouse.product_unit.product.id: record}
                    )

        content = JSONRenderer().render(
            ProductSerializer(result.values(), many=True).data
        )

        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)

        self.send(text_data=json.dumps({"message": data}))
