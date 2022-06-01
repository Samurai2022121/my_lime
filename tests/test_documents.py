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
def django_db_setup(request, django_db_setup):
    # load a fixture from current directory
    call_command(
        "loaddata",
        Path(request.fspath).parent / "fixtures" / "shops.json",
        Path(request.fspath).parent / "fixtures" / "units.json",
        Path(request.fspath).parent / "fixtures" / "warehouses.json",
        Path(request.fspath).parent / "fixtures" / "suppliers.json",
        Path(request.fspath).parent / "fixtures" / "batches.json",
    )


class TestInventoryDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
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

        def test_record_list(self, json, client):
            """Test inventory records created."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:inventoryrecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 4

    class TestCreateWithExistingBatches(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "warehouse_records": [
                    {
                        "product_unit": 1,
                        "quantity": 100,
                        "price": "99.95",
                        "batch": 1,
                    },
                    {
                        "product_unit": 2,
                        "quantity": 50,
                        "price": "48.50",
                        "batch": 2,
                    },
                ],
            }
        )

        def test_batch_count(self, json, client):
            result = client.get(url_for("internal_api:batch-list"))
            # no extra batches
            assert result.json()["count"] == 2

    class TestCreateWithNewBatches(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "warehouse_records": [
                    {
                        "product_unit": 1,
                        "quantity": 100,
                        "price": "99.95",
                        "supplier": 1,
                        "production_date": "2022-01-01",
                        "expiration_date": "2022-01-01",
                    },
                    {
                        "product_unit": 2,
                        "quantity": 50,
                        "price": "48.50",
                        "supplier": 1,
                    },
                ],
            }
        )

        def test_batch_count(self, json, client):
            result = client.get(url_for("internal_api:batch-list"))
            # two extra batches created
            assert result.json()["count"] == 4


class TestReceiptDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, load_order, staff_client, get_response):
        return get_response

    @pytest.fixture
    def load_order(self, request):
        # load order
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

        def test_record_list(self, json, client):
            """Test receipt records created."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:receiptrecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 4

    class TestCreateWithExistingBatches(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "order": 1,
                "warehouse_records": [
                    {
                        "product_unit": 1,
                        "quantity": 100,
                        "price": "99.95",
                        "batch": 1,
                    },
                    {
                        "product_unit": 2,
                        "quantity": 50,
                        "price": "48.50",
                        "batch": 2,
                    },
                ],
            }
        )

        def test_batch_count(self, json, client):
            result = client.get(url_for("internal_api:batch-list"))
            # no extra batches
            assert result.json()["count"] == 2

    class TestCreateWithNewBatches(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "shop": 1,
                "order": 1,
                "warehouse_records": [
                    {
                        "product_unit": 3,
                        "quantity": 25,
                        "price": "23.32",
                        "supplier": 1,
                    },
                    {
                        "product_unit": 4,
                        "quantity": 13,
                        "price": "23.32",
                        "supplier": 1,
                        "production_date": "2022-01-01",
                        "expiration_date": "2022-01-01",
                    },
                ],
            }
        )

        def test_batch_count(self, json, client):
            result = client.get(url_for("internal_api:batch-list"))
            # two extra batches created
            assert result.json()["count"] == 4


class TestWriteOffDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

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
                        "batch": 1,
                    },
                ],
            }
        )

        def test_record_list(self, json, client):
            """Test write off records created."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:writeoffrecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 1


class TestReturnDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

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
                        "batch": 1,
                    },
                ],
            }
        )

        def test_record_list(self, json, client):
            """Test return records created."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:returnrecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 1


class TestConversionDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, create_conversion, staff_client, get_response):
        return get_response

    @pytest.fixture
    def create_conversion(self, staff_client):
        # add a converter for "Товар для разукомплектации" ("кор." -> "г")
        result = staff_client.post(
            url_for("products:targets-list", product_id=3, unit_id=4),
            data={
                "source_unit": 3,
                "factor": 300.0,
            },
            format="json",
        )
        assert result.status_code == status.HTTP_201_CREATED

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

        def test_record_list(self, json, client):
            """Test conversion records created (two for each input line)."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:conversionrecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 2


class TestMoveDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

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
                        "batch": 1,
                    },
                    {
                        "warehouse": 2,
                        "quantity": 15,
                        "batch": 2,
                    },
                ],
            }
        )

        def test_record_list(self, json, client):
            """Test move records created (two for each input line)."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:moverecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 4


class TestSaleDocumentViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, authenticated_client, get_response):
        return get_response

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
                        "batch": 1,
                    },
                    {
                        "warehouse": 2,
                        "quantity": 15,
                        "batch": 2,
                    },
                ],
            }
        )

        def test_implied_author(self, json):
            # authenticated user ID
            assert json["author"] == 3

        def test_record_list(self, json, client):
            """Test sale records created."""
            document_id = json["id"]
            record_list_url = url_for(
                "internal_api:salerecord-list",
                document_id,
            )
            result = client.get(record_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 2

    class TestCreateWithAuthor(UsesPostMethod, UsesListEndpoint, Returns201):
        @pytest.fixture
        def common_subject(self, db, admin_client, get_response):
            return get_response

        data = static_fixture({"shop": 1, "author": 3, "warehouse_records": []})

        def test_author(self, json):
            #  directly provided user ID
            assert json["author"] == 3
