from pathlib import Path

import pytest
from django.core.management import call_command
from pytest_drf import (
    Returns200,
    Returns201,
    Returns400,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework import status

from utils.views_utils import ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup):
    call_command(
        "loaddata",
        Path(request.fspath).parent / "fixtures" / "products.json",
        Path(request.fspath).parent / "fixtures" / "shops.json",
        Path(request.fspath).parent / "fixtures" / "units.json",
        Path(request.fspath).parent / "fixtures" / "discounts.json",
    )


class TestRangesViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("discounts:range-list"))

    detail_url = lambda_fixture(lambda id: url_for("discounts:range-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        data = static_fixture(
            {
                "name": "Test create range",
                "includes_all": True,
            }
        )


class TestOffersViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("discounts:offer-list"))

    detail_url = lambda_fixture(lambda id: url_for("discounts:offer-detail", id=id))

    class TestFullList(UsesGetMethod, UsesListEndpoint, Returns200):
        def test_result_count(self, json):
            assert json["count"] == 5

    class TestTextSearch(UsesGetMethod, UsesListEndpoint, Returns200):
        @pytest.fixture
        def list_url(self, list_url):
            return list_url + "?s=хлеб"

        def test_result_count(self, json):
            assert json["count"] == 1

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)

    class TestUpdate(UsesPatchMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        id = static_fixture(1)
        data = static_fixture({"condition": {"range": 4}})

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        data = static_fixture(
            {
                "condition": {"type": "value", "value": "50.00", "range": 4},
                "benefit": {"type": "percentage", "value": "5.00", "range": 3},
                "name": "Проверка создания предложения",
                "type": "site",
            }
        )

    class TestApplySiteOffer(UsesPostMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        detail_url = lambda_fixture(lambda id: url_for("discounts:offer-apply", id=id))
        id = static_fixture(1)

    class TestApplyBuyerOffer(UsesPostMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        detail_url = lambda_fixture(lambda id: url_for("discounts:offer-apply", id=id))
        id = static_fixture(5)
        data = static_fixture({"phone_number": "79010060000"})

        def test_buyer_count(self, authenticated_client, json):
            offer_id = json["id"]
            buyer_count_list_url = url_for(
                "discounts:buyercount-list", offer_id=offer_id
            )
            result = authenticated_client.get(buyer_count_list_url)
            assert result.status_code == status.HTTP_200_OK
            assert len(result.json()["results"]) == 1

    class TestApplyWrongOffer(UsesPostMethod, UsesListEndpoint, Returns400):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        detail_url = lambda_fixture(lambda id: url_for("discounts:offer-apply", id=id))
        id = static_fixture(3)


class TestVouchersViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("discounts:voucher-list"))

    detail_url = lambda_fixture(lambda id: url_for("discounts:voucher-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture("0170649a-5f45-4eeb-9b11-36b9eba338e2")

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture({"offer": 2})

    class TestCreateWrongOffer(UsesPostMethod, UsesListEndpoint, Returns400):
        data = static_fixture({"offer": 1})

    class TestUpdate(UsesPatchMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture("0170649a-5f45-4eeb-9b11-36b9eba338e2")
        data = static_fixture({"is_active": False})

    class TestUpdateWrongOffer(UsesPatchMethod, UsesDetailEndpoint, Returns400):
        id = static_fixture("0170649a-5f45-4eeb-9b11-36b9eba338e2")
        data = static_fixture({"offer": 1})

    class TestApply(UsesPostMethod, UsesDetailEndpoint, Returns200):
        detail_url = lambda_fixture(
            lambda id: url_for("discounts:voucher-apply", id=id)
        )
        id = static_fixture("0170649a-5f45-4eeb-9b11-36b9eba338e2")

    class TestApplyInactiveVoucher(UsesPostMethod, UsesDetailEndpoint, Returns400):
        detail_url = lambda_fixture(
            lambda id: url_for("discounts:voucher-apply", id=id)
        )
        id = static_fixture("4cd6fbd4-2597-4751-b555-d653b4640410")

    class TestApplyInactiveOffer(UsesPostMethod, UsesDetailEndpoint, Returns400):
        detail_url = lambda_fixture(
            lambda id: url_for("discounts:voucher-apply", id=id)
        )
        id = static_fixture("6bb5544d-9248-47ad-a4a0-7f34bdbdd4fc")


class TestLoyaltyCardsViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, authenticated_client, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("discounts:loyaltycard-list"))

    detail_url = lambda_fixture(
        lambda id: url_for("discounts:loyaltycard-detail", id=id)
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        data = static_fixture({"buyer": 2, "offer": 4})

    class TestCreateWrongOffer(UsesPostMethod, UsesListEndpoint, Returns400):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        data = static_fixture({"buyer": 1, "offer": 1})

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture("69e0a2a6-cacc-4b39-a7b3-02a2759160ac")

    class TestApply(UsesPostMethod, UsesDetailEndpoint, Returns200):
        @pytest.fixture
        def common_subject(self, staff_client, get_response):
            return get_response

        detail_url = lambda_fixture(
            lambda id: url_for("discounts:loyaltycard-apply", id=id)
        )
        id = static_fixture("69e0a2a6-cacc-4b39-a7b3-02a2759160ac")
