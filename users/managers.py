from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, phone_number, password, is_staff, is_superuser, email=None, **extra_fields
    ):
        if not phone_number:
            raise ValueError(_("The Phone Number must be set"))
        if not password:
            raise ValueError(_("The Password must be set"))

        email = self.normalize_email(email) if email else None
        user = self.model(
            email=email,
            phone_number=phone_number,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password, **extra_fields):
        return self._create_user(phone_number, password, False, False, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        return self._create_user(phone_number, password, True, True, **extra_fields)
