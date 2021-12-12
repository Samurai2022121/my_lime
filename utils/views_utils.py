from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        response = super(ProductPagination, self).get_paginated_response(data)
        response.data["total_pages"] = self.page.paginator.num_pages
        return response


class OrderingModelViewsetMixin:
    def get_ordering_fields(self):
        order_by_str = self.request.query_params.get("order_by")
        order_by_parts = order_by_str.split(",") if order_by_str else []

        ordering_values = []

        for orderby_part in order_by_parts:
            if not orderby_part:
                continue
            parts = orderby_part.split("-")
            field = parts[1] if len(parts) == 2 else parts[0]
            if hasattr(self.queryset.model, field):
                ordering_values.append(orderby_part)
        return ordering_values


class BulkUpdateViewSetMixin(object):
    @action(detail=False, methods=["post"], url_path="bulk_update")
    def bulk_update(self, request, **kwargs):
        serializer = self.get_serializer_class()
        serialized_data = serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        for instance in instances:
            self.queryset.filter(id=instance.pop("id")).update(**instance)
        return Response(status=status.HTTP_200_OK)
