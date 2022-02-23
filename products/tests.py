from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    Returns204,
    Returns404,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
    ViewSetTest,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", Path(request.fspath).parent / "test_unit_api.json")
    yield
    with django_db_blocker.unblock():
        call_command("flush", "--no-input")


class TestMeasurementUnitViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("products:measurementunit-list"))

    detail_url = lambda_fixture(
        lambda unit_id: url_for("products:measurementunit-detail", unit_id)
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        pass

    class TestRetrieveExistingUnit(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        unit_id = static_fixture(1)

    class TestRetrieveNonExistingShop(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns404,
    ):
        unit_id = static_fixture(99)

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        data = static_fixture({"name": "NewUnit"})

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        unit_id = static_fixture(3)
        data = static_fixture({"name": "AnotherUnitName"})

    class TestDelete(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns204,
    ):
        unit_id = static_fixture(3)


class TestProductUnitViewset(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(
        lambda product_id: url_for("products:productunit-list", product_id)
    )

    detail_url = lambda_fixture(
        lambda product_id, id: url_for("products:productunit-detail", product_id, id)
    )

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        product_id = static_fixture(2)

    class TestRetrieveUnit(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        product_id = static_fixture(3)
        id = static_fixture(4)

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
    ):
        product_id = static_fixture(1)
        data = static_fixture({"unit": "Кор."})

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        product_id = static_fixture(2)
        id = static_fixture(2)
        data = static_fixture({"for_resale": True})
