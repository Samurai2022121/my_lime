from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    Returns404,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup, django_db_blocker):
    # load a fixture from current directory
    with django_db_blocker.unblock():
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "shops.json",
        )
    yield
    with django_db_blocker.unblock():
        call_command("flush", "--no-input")


class TestShopViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        # this test set is going to use database
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
    def common_subject(self, db, django_db_blocker, request, get_response):
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "units.json",
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

    data = static_fixture(
        {
            "product_unit": 1,
            "price": Decimal("20.22"),
        }
    )

    shop_id = static_fixture(1)

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def id(self, client, list_url, data):
            result = client.post(list_url, data)
            return result.json()["id"]


class TestWarehouseRecordViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, django_db_blocker, request, get_response):
        with django_db_blocker.unblock():
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
