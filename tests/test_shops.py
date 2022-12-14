from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    Returns400,
    Returns404,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture

from utils.views_utils import ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup):
    # load a fixture from current directory
    call_command(
        "loaddata",
        Path(request.fspath).parent / "fixtures" / "shops.json",
    )


class TestShopViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        # use database, run as staff
        return get_response

    list_url = lambda_fixture(lambda: url_for("internal_api:shop-list"))

    detail_url = lambda_fixture(
        lambda shop_id: url_for("internal_api:shop-detail", shop_id)
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        # check if list endpoint returns 200
        pass

    class TestRetrieveExistingShop(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        # check if detail endpoint returns 200
        shop_id = static_fixture(1)  # this Id is in fixture

    class TestRetrieveNonExistingShop(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns404,
    ):
        # check if detail endpoint returns 404
        shop_id = static_fixture(99)  # this Id is not in fixture


class TestWarehouseViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, request, staff_client, get_response):
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "units.json",
            Path(request.fspath).parent / "fixtures" / "warehouses.json",
        )
        return get_response

    list_url = lambda_fixture(
        lambda shop_id: url_for("internal_api:warehouse-list", shop_id=shop_id)
    )

    detail_url = lambda_fixture(
        lambda shop_id, id: url_for(
            "internal_api:warehouse-detail",
            shop_id=shop_id,
            id=id,
        )
    )

    shop_id = static_fixture(1)

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestOrderBy(UsesGetMethod, UsesListEndpoint, Returns200):
        @pytest.fixture
        def list_url(self, list_url):
            return list_url + "?order_by=product_name"

        def test_first_result(self, json):
            assert json[0]["product_unit"]["product"]["name"] == "???????????????? ??????????"

    class TestCreateDuplicate(UsesPostMethod, UsesListEndpoint, Returns400):
        data = static_fixture(
            {
                "product_unit": 1,
                "price": Decimal("20.22"),
            }
        )

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "product_unit": 5,
                "price": Decimal("20.22"),
            }
        )

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)


class TestWarehouseRecordViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, request, staff_client, get_response):
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "units.json",
            Path(request.fspath).parent / "fixtures" / "warehouses.json",
        )
        return get_response

    list_url = lambda_fixture(
        lambda shop_id, warehouse_id: url_for(
            "internal_api:warehouserecord-list",
            shop_id=shop_id,
            warehouse_id=warehouse_id,
        )
    )

    detail_url = lambda_fixture(
        lambda shop_id, warehouse_id, id: url_for(
            "internal_api:warehouserecord-detail",
            shop_id=shop_id,
            warehouse_id=warehouse_id,
            id=id,
        )
    )

    data = static_fixture(
        {
            "quantity": -1,
            "document": 1,
        }
    )

    shop_id = static_fixture(1)

    warehouse_id = static_fixture(1)

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def id(self, client, list_url, data):
            result = client.post(list_url, data)
            return result.json()["id"]
