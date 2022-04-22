from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from pytest_drf import Returns200, Returns403, UsesListEndpoint, UsesPostMethod
from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture
from rest_framework.authtoken.models import Token

from utils.views_utils import APIViewTest


@pytest.fixture(scope="module")
def django_db_setup(request, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command(
            "loaddata", Path(request.fspath).parent / "fixtures" / "users.json"
        )
        yield
        call_command("flush", "--no-input")


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
