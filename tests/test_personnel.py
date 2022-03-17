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
    UsesPutMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture

from utils.views_utils import ViewSetTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command(
            "loaddata",
            Path(request.fspath).parent / "fixtures" / "users.json",
            Path(request.fspath).parent / "fixtures" / "shops.json",
            Path(request.fspath).parent / "fixtures" / "personnel.json",
        )
    yield
    with django_db_blocker.unblock():
        call_command("flush", "--no-input")


class TestPositionViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("personnel:position-list"))

    detail_url = lambda_fixture(lambda id: url_for("personnel:position-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        data = static_fixture(
            {
                "name": "Abracadabra",
            }
        )


class TestPersonnelViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("personnel:personnel-list"))

    detail_url = lambda_fixture(lambda id: url_for("personnel:personnel-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(1)

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        # so that "Content-type" may default to "multipart/form-data"
        format = static_fixture(None)

        @pytest.fixture
        def data(wojak):
            return {
                "user": 2,
                "position": "Кассир",
                "phone_number": "9070060009",
                "contract_period": 1,
                "contract_type": "fefe",
                "workplaces": [2],
                "avatar": wojak,
            }


class TestPassportViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(
        lambda personnel_id: url_for(
            "personnel:localpassport-list",
            personnel_id=personnel_id,
        )
    )

    detail_url = lambda_fixture(
        lambda personnel_id, id: url_for(
            "personnel:localpassport-detail",
            personnel_id=personnel_id,
            id=id,
        )
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        personnel_id = static_fixture(1)

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        personnel_id = static_fixture(1)

        data = static_fixture(
            {
                "first_name": "Иван",
                "patronymic": "Иванович",
                "last_name": "Иванов-Вано",
                "date_of_birth": "1952-03-01",
                "identification_number": "98368756755421",
                "issued_by": "Дзержинский райисполком",
                "issued_at": "2016-03-01",
                "valid_until": "2024-03-01",
            }
        )

    class TestUpdate(UsesPutMethod, UsesDetailEndpoint, Returns200):
        personnel_id = static_fixture(1)

        id = static_fixture(1)

        data = static_fixture(
            {
                "first_name": "Иоганн",
                "patronymic": "Иванович",
                "last_name": "Иванов-Вано",
                "date_of_birth": "1952-03-01",
                "identification_number": "98368756755421",
                "issued_by": "Дзержинский райисполком",
                "issued_at": "2016-03-01",
                "valid_until": "2024-03-01",
            }
        )


class TestPersonnelDocumentViewSet(ViewSetTest):
    @pytest.fixture
    def common_subject(self, db, get_response):
        return get_response

    list_url = lambda_fixture(
        lambda personnel_id: url_for(
            "personnel:personneldocument-list",
            personnel_id=personnel_id,
        )
    )

    detail_url = lambda_fixture(
        lambda personnel_id, id: url_for(
            "personnel:personneldocument-detail",
            personnel_id=personnel_id,
            id=id,
        )
    )

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        personnel_id = static_fixture(1)

    class TestCreate(UsesPostMethod, UsesListEndpoint, Returns201):
        format = static_fixture(None)

        personnel_id = static_fixture(1)

        @pytest.fixture
        def data(self, pepe):
            return {
                "number": "JRGH9580",
                "personnel_document": pepe,
            }
