from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework import status

from utils.views_utils import ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup, django_db_blocker):
    # load a fixture from current directory
    with django_db_blocker.unblock():
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "shops.json",
            Path(request.fspath).parent / "fixtures" / "units.json",
        )
    yield
    with django_db_blocker.unblock():
        call_command("flush", "--no-input")


class TestInventoryDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("internal_api:inventorydocument-list"))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "warehouse_records": [
                    {
                        "product_unit": 1,
                        "quantity": 100,
                        "price": "99.95",
                    },
                    {
                        "product_unit": 2,
                        "quantity": 50,
                        "price": "48.50",
                    },
                    {
                        "product_unit": 3,
                        "quantity": 25,
                        "price": "23.32",
                    },
                    {
                        "product_unit": 4,
                        "quantity": 13,
                        "price": "23.32",
                    },
                ],
            }
        )


class TestReceiptDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_order, get_response):
        return get_response

    @pytest.fixture
    def load_order(self, request, django_db_blocker):
        # load order
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "orders.json",
            )

    list_url = lambda_fixture(lambda: url_for("internal_api:receiptdocument-list"))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "order": 1,
                "warehouse_records": [
                    {
                        "product_unit": 1,
                        "quantity": 100,
                        "price": "99.95",
                    },
                    {
                        "product_unit": 2,
                        "quantity": 50,
                        "price": "48.50",
                    },
                    {
                        "product_unit": 3,
                        "quantity": 25,
                        "price": "23.32",
                    },
                    {
                        "product_unit": 4,
                        "quantity": 13,
                        "price": "23.32",
                    },
                ],
            }
        )


class TestWriteOffDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_inventory, get_response):
        return get_response

    @pytest.fixture
    def load_inventory(self, request, django_db_blocker):
        # load inventory data (as in previous test)
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "warehouses.json",
            )

    list_url = lambda_fixture(lambda: url_for("internal_api:writeoffdocument-list"))

    detail_url = lambda_fixture(
        lambda pk: url_for("internal_api:writeoffdocument-detail", pk)
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "warehouse_records": [
                    {
                        "warehouse": 1,
                        "quantity": 13,
                    },
                ],
            }
        )


class TestReturnDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_inventory, get_response):
        return get_response

    @pytest.fixture
    def load_inventory(self, request, django_db_blocker):
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "warehouses.json",
            )

    list_url = lambda_fixture(lambda: url_for("internal_api:returndocument-list"))

    detail_url = lambda_fixture(
        lambda pk: url_for("internal_api:returndocument-detail", pk)
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "warehouse_records": [
                    {
                        "warehouse": 1,
                        "quantity": 13,
                    },
                ],
            }
        )


class TestConversionDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_inventory, create_conversion, get_response):
        return get_response

    @pytest.fixture
    def create_conversion(self, client):
        # add a converter for "Товар для разукомплектации" ("кор." -> "г")
        result = client.post(
            url_for("products:targets-list", product_id=3, unit_id=4),
            data={
                "source_unit": 3,
                "factor": 300.0,
            },
            format="json",
        )
        assert result.status_code == status.HTTP_201_CREATED

    @pytest.fixture
    def load_inventory(self, request, django_db_blocker):
        # load inventory data (as in previous test)
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "warehouses.json",
            )

    list_url = lambda_fixture(lambda: url_for("internal_api:conversiondocument-list"))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "warehouse_records": [
                    {
                        "warehouse": 4,
                        "quantity": 13,
                        "target_unit": 4,
                    },
                ],
            }
        )


class TestMoveDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_inventory, get_response):
        return get_response

    @pytest.fixture
    def load_inventory(self, request, django_db_blocker):
        # load inventory data (as in previous test)
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "warehouses.json",
            )

    list_url = lambda_fixture(lambda: url_for("internal_api:movedocument-list"))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "target_shop": 2,
                "warehouse_records": [
                    {
                        "warehouse": 1,
                        "quantity": 30,
                    },
                    {
                        "warehouse": 2,
                        "quantity": 15,
                    },
                ],
            }
        )


class TestSaleDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_inventory, get_response):
        return get_response

    @pytest.fixture
    def load_inventory(self, request, django_db_blocker):
        # load inventory data (as in previous test)
        with django_db_blocker.unblock():
            call_command(
                "loaddata",
                Path(request.fspath).parent / "fixtures" / "warehouses.json",
            )

    list_url = lambda_fixture(lambda: url_for("internal_api:saledocument-list"))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "warehouse_records": [
                    {
                        "warehouse": 1,
                        "quantity": 30,
                    },
                    {
                        "warehouse": 2,
                        "quantity": 15,
                    },
                ],
            }
        )
