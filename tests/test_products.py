from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework.status import HTTP_200_OK

CATEGORY_ID = 2


class TestProductViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, request, db, get_response):
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "products.json",
        )
        return get_response

    list_url = lambda_fixture(lambda: url_for("internal_api:product-list"))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        def test_number(self, json):
            # all but non-revised and archived
            assert len(json["results"]) == 6

    class TestUnfilteredList(UsesGetMethod, UsesListEndpoint, Returns200):
        list_url = lambda_fixture(
            lambda: url_for("internal_api:product-list")
            + "?is_archive=all&is_sorted=all"
        )

        def test_number(self, json):
            # all products
            assert len(json["results"]) == 8

    class TestUnsortedList(UsesGetMethod, UsesListEndpoint, Returns200):
        list_url = lambda_fixture(
            lambda: url_for("internal_api:product-list") + "?is_sorted=false"
        )

        def test_number(self, json):
            # non-revised only
            assert len(json["results"]) == 1

    class TestArchivedList(UsesGetMethod, UsesListEndpoint, Returns200):
        list_url = lambda_fixture(
            lambda: url_for("internal_api:product-list") + "?is_archive=true"
        )

        def test_number(self, json):
            # archived only
            assert len(json["results"]) == 1

    @pytest.mark.parametrize("cat_id,number", [(1, 4), (2, 2), (9, 2), (4, 1)])
    class TestInCategoryList(UsesGetMethod, UsesListEndpoint):
        @pytest.fixture
        def list_url(self, cat_id):
            return url_for("internal_api:product-list") + f"?category={cat_id}"

        def test_status(self, number, response):
            # this test just wants to be parameterized for no good reason
            assert response.status_code == HTTP_200_OK

        def test_number(self, json, number):
            # all products in "cat_id" category and subcategories
            assert len(json["results"]) == number

    class TestSearchList(UsesGetMethod, UsesListEndpoint, Returns200):
        # the search should return something
        list_url = lambda_fixture(
            lambda: url_for("internal_api:product-list") + "?s=товар"
        )

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        @pytest.fixture
        def client(self, staff_client):
            return staff_client

        data = static_fixture(
            {
                "name": "Test product",
                "barcode": "1234567890123",
                "manufacturer": "ACME Co. Ltd",
                "price": 11.05,
                "for_scales": False,
            }
        )


class TestProductCategoryViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, request, db, get_response):
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "products.json",
        )
        return get_response

    list_url = lambda_fixture(lambda: url_for("products:category-list"))

    detail_url = lambda_fixture(lambda id: url_for("products:category-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        @pytest.fixture
        def client(self, staff_client):
            return staff_client

        format = static_fixture(None)

        @pytest.fixture
        def data(self, wojak):
            return {
                "name": "Test Category 33",
                "parent_id": 4,
                "image": wojak,
            }

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(4)
