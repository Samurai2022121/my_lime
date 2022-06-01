from functools import partial

import pytest
from django.db.models import Q
from pytest_drf import views as test_views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers_utils import BulkActionSerializer, BulkUpdateSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        response = super(DefaultPagination, self).get_paginated_response(data)
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
            if field.find("supplier__name") != (-1):
                ordering_values.append(orderby_part)
            elif hasattr(self.queryset.model, field):
                ordering_values.append(orderby_part)
        return ordering_values


class BulkUpdateViewSetMixin:
    @action(detail=False, methods=["post"], url_path="bulk_update")
    def bulk_update(self, request, **kwargs):
        serialized_data = BulkUpdateSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        for instance in instances:
            self.queryset.filter(id=instance.pop("id")).update(**instance)
        return Response(status=status.HTTP_200_OK)


class ChangeDestroyToArchiveMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_archive = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkChangeArchiveStatusViewSetMixin:
    @action(detail=False, methods=["post"], url_path="bulk-archive")
    def change_archive_status(self, request, **kwargs):
        serialized_data = BulkActionSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        instances = serialized_data.data["instances"]
        self.queryset.filter(id__in=instances).update(is_archive=Q(is_archive=False))
        return Response(status=status.HTTP_200_OK)


class APIViewTest(test_views.APIViewTest):
    """Temporary workaround (possible pytest-django or drf bug)."""

    @pytest.fixture
    def format(self):
        # request format (JSON by default)
        return "json"

    @pytest.fixture
    def get_response(self, http_method, format, client):
        # set request format
        return partial(getattr(client, http_method), format=format)


class ViewSetTest(APIViewTest):
    """Taken from 'pytest-drf'."""

    @pytest.fixture
    def list_url(self):
        raise NotImplementedError("Please define a list_url fixture")

    @pytest.fixture
    def detail_url(self):
        raise NotImplementedError("Please define a detail_url fixture")
