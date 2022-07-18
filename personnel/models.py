from datetime import date
from secrets import token_hex

from django.conf import settings
from django.db import models

from internal_api.models import Shop
from utils.choices import Choices
from utils.models_utils import Timestampable, phone_regex


class Position(models.Model):
    name = models.CharField("наименование", unique=True, max_length=255)

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self):
        return self.name


class Personnel(models.Model):
    WORK_STATUS = Choices(
        ("working", "Работает"),
        ("fired", "Уволен"),
        ("vacation", "Отпуск"),
        ("maternity_leave", "Декрет"),
        ("probation", "Испытательный срок"),
        ("archived", "Архивный"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="пользователь",
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        verbose_name="должность",
    )
    workplaces = models.ManyToManyField(Shop, verbose_name="рабочие места")
    phone_number = models.CharField(
        "телефон",
        validators=[phone_regex],
        max_length=17,
    )
    hired_at = models.DateTimeField("дата найма", auto_now=True)
    status = models.CharField(
        "статус",
        max_length=255,
        choices=WORK_STATUS,
        default=WORK_STATUS.probation,
    )
    photo = models.ImageField(
        "фото",
        upload_to="internal-api/staff/",
        null=True,
        blank=True,
    )
    contract_period = models.IntegerField("срок действия договора")
    contract_type = models.CharField("тип договора", max_length=255)

    class Meta:
        verbose_name = "Личная карточка"
        verbose_name_plural = "Личные карточки"
        default_related_name = "personnel"

    def __str__(self):
        passport = self.local_passports.filter(active=True).last()
        if passport:
            return passport.__str__()

        if self.user:
            return self.user.get_full_name()

        return "Unknown employee"


class LocalPassport(models.Model):
    employee = models.ForeignKey(
        Personnel,
        on_delete=models.CASCADE,
        related_name="local_passports",
        verbose_name="работник",
    )
    active = models.BooleanField("действителен", default=True)
    first_name = models.CharField("имя", max_length=255)
    last_name = models.CharField("фамилия", max_length=255)
    patronymic = models.CharField("отчество", max_length=255, null=True, blank=True)
    date_of_birth = models.DateField("дата рождения")
    place_of_birth = models.CharField(
        "место рождения",
        max_length=255,
        null=True,
        blank=True,
    )
    identification_number = models.CharField(
        "личный номер",
        max_length=14,
        unique=True,
    )
    issued_by = models.CharField("орган, выдавший паспорт", max_length=255)
    issued_at = models.DateField("дата выдачи")
    valid_until = models.DateField("срок действия")

    class Meta:
        verbose_name = "Паспорт"
        verbose_name_plural = "Паспорты"
        ordering = ("issued_by",)

    def __str__(self):
        return " ".join([self.first_name, self.patronymic, self.last_name])


def create_personnel_document_download_path(instance, filename):
    directory = "internal-api/personal-documents/"
    upload_date = date.today().strftime("%d%M%Y")
    salt = token_hex(5)
    return f"{directory}_{upload_date}_{salt}_{filename}"


class PersonnelDocument(Timestampable, models.Model):
    employee = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT,
        related_name="personnel_documents",
        verbose_name="работник",
        null=True,
        blank=True,
    )
    personnel_document = models.FileField(
        "файл документа",
        null=True,
        blank=True,
        upload_to=create_personnel_document_download_path,
    )
    number = models.CharField("номер", max_length=255)
    date = models.DateField("дата", auto_now_add=True, editable=True)

    class Meta:
        verbose_name = "Документ работника"
        verbose_name_plural = "Документы работников"
