import uuid as uuid
from datetime import datetime

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as BaseGroup
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.models_utils import compress_image, generate_new_password, phone_regex

from .managers import CustomUserManager


class Group(BaseGroup):
    class Meta:
        proxy = True
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True, verbose_name="Телефон"
    )
    email = models.EmailField(_("email address"), null=True, blank=True)
    name = models.CharField(max_length=40, null=True, blank=True, verbose_name="Имя")
    surname = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Фамилия"
    )
    fathers_name = models.CharField(
        max_length=40, null=True, blank=True, verbose_name="Отчество"
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name="День рождения"
    )
    avatar = models.ImageField(null=True, blank=True, verbose_name="Аватар")
    registration_date = models.DateTimeField(auto_now=True)
    is_archive = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()}"

    def save(self, *args, **kwargs):
        self.phone_number = self.phone_number.replace("+", "")
        if self.avatar:
            self.avatar = compress_image(
                self.avatar, (500, 500), "avatar", ("jpeg", "jpg")
            )
        super(User, self).save()

    def get_full_name(self):
        if self.name:
            return f"{self.name} {self.surname}" if self.surname else self.name
        else:
            return self.phone_number

    def get_short_name(self):
        return self.name if self.name else "Anonymous user"

    def generate_tokens(self):
        expires_in = int(
            datetime.timestamp(timezone.now() + settings.ACCESS_TOKEN_LIFETIME)
        )
        access = jwt.encode(
            {"id": self.pk, "expires_in": expires_in},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        refresh = RefreshToken(user=self)
        refresh.save()
        return {
            "access": access,
            "refresh": refresh.uuid,
            "expires_in": expires_in,
            "phone": self.phone_number,
        }


class RefreshToken(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        default_related_name = "refresh_token"

    def __str__(self):
        return f"Refresh {str(self.user)}"


class GeneratedPassword(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.CharField(
        default=generate_new_password, editable=False, max_length=8
    )
    attempts = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date", "is_active"]
        verbose_name = "временный пароль"
        verbose_name_plural = "временные пароли"

    def __str__(self):
        return f"Generated password for {str(self.user)}"


class CustomerDeliveryAddress(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="delivery_address"
    )
    locality = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house = models.PositiveIntegerField()
    block = models.CharField(max_length=255, null=True, blank=True)
    entrance = models.PositiveIntegerField(null=True, blank=True)
    floor = models.PositiveIntegerField(null=True, blank=True)
    apartment = models.CharField(max_length=255, null=True, blank=True)
    additional_information = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()
    is_archive = models.BooleanField(default=False)
