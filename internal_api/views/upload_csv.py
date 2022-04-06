from decimal import Decimal

import pandas as pd
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED

from products.models import Product
from products.serializers import ProductListSerializer

from .. import serializers


class UploadCSVGenericView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UploadCSVSerializer
    queryset = Product.objects.all()

    product_fields_mapping = {
        "price_col": "price",
        "name_col": "name",
        "barcode_col": "barcode",
        "vat_col": "vat_value",
        "measure_unit_col": "measure_unit",
        "origin_col": "origin",
        "supplier_col": "manufacturer",
    }

    def post(self, request):
        context = {"request": request}

        serialized_data = self.serializer_class(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        data = serialized_data.validated_data

        file = pd.read_excel(data.get("csv_file", None), engine="openpyxl")

        file = file.where(pd.notnull(file), None)
        products = []
        row_num = data.get("first_row", None)

        for _, row in file.iloc[row_num:].iterrows():

            if row[data.get("name_col", 0)] and row[data.get("price_col", 0)]:

                name = row[data.get("name_col", None)]
                price = Decimal(row[data.get("price_col", None)])
                products.append(
                    Product(
                        name=name,
                        price=price,
                        barcode=row[data["barcode_col"]]
                        if data.get("barcode_col", None)
                        else None,
                        vat_value=str(row[data["vat_col"]]).replace("%", "")
                        if data.get("vat_col", None)
                        else None,
                        measure_unit=row[data["measure_unit_col"]]
                        # TODO: fix creation of measurement units
                        if data.get("measure_unit_col", None) else None,
                        origin=row[data["origin_col"]]
                        if data.get("origin_col", None)
                        else None,
                        manufacturer=row[data["supplier_col"]]
                        if data.get("supplier_col", None)
                        else None,
                    )
                )

        created_products = Product.objects.bulk_create(products, ignore_conflicts=True)
        serializer = ProductListSerializer(created_products, many=True, context=context)

        return Response(status=HTTP_202_ACCEPTED, data=serializer.data)
