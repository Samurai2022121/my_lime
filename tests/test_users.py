import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from pytest_drf import (
    Returns200,
    Returns403,
    UsesDetailEndpoint,
    UsesGetMethod,
    UsesListEndpoint,
    UsesPostMethod,
)
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework.authtoken.models import Token

from utils.views_utils import APIViewTest


class TestObtainPlainTokenForSuperuser(
    APIViewTest,
    UsesListEndpoint,
    UsesPostMethod,
    Returns200,
):
    @pytest.fixture
    def common_subject(self, db, user, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("users:obtain-plain"))

    @pytest.fixture
    def user(self):
        user = get_user_model().objects.get(phone_number="79010000000")
        user.set_password("superuser_password")
        user.save()
        return user

    data = static_fixture(
        {
            "phone_number": "79010000000",
            "password": "superuser_password",
        }
    )


class TestObtainPlainTokenForPlainUserser(
    APIViewTest,
    UsesListEndpoint,
    UsesPostMethod,
    Returns403,
):
    @pytest.fixture
    def common_subject(self, db, user, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("users:obtain-plain"))

    @pytest.fixture
    def user(self):
        user = get_user_model().objects.get(phone_number="79010060000")
        user.set_password("plain_user_password")
        user.save()
        return user

    data = static_fixture(
        {
            "phone_number": "79010060000",
            "password": "plain_user_password",
        }
    )


class TestObtainPlainTokenForAuthorizedUserser(
    APIViewTest,
    UsesListEndpoint,
    UsesPostMethod,
    Returns200,
):
    @pytest.fixture
    def common_subject(self, db, user, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("users:obtain-plain"))

    @pytest.fixture
    def user(self):
        user = get_user_model().objects.get(phone_number="79010060000")
        user.set_password("plain_user_password")
        user.save()
        perm = Permission.objects.get(
            content_type__app_label=f"{Token._meta.app_label}",
            codename=f"add_{Token._meta.model_name}",
        )
        user.user_permissions.add(perm)
        user.refresh_from_db()
        return user

    data = static_fixture(
        {
            "phone_number": "79010060000",
            "password": "plain_user_password",
        }
    )


class TestUserViewSet(APIViewTest):
    @pytest.fixture
    def common_subject(self, db, staff_client, get_response):
        return get_response

    list_url = lambda_fixture(lambda: url_for("users:user-list"))

    detail_url = lambda_fixture(lambda id: url_for("users:user-detail", id=id))

    class TestList(UsesGetMethod, UsesListEndpoint, Returns200):
        pass

    class TestDetail(UsesGetMethod, UsesDetailEndpoint, Returns200):
        id = static_fixture(3)

    class TestGetCurrendUser(UsesGetMethod, Returns200):
        @pytest.fixture
        def common_subject(self, authenticated_client, get_response):
            return get_response

        url = lambda_fixture(lambda: url_for("users:user-get-current-user"))
