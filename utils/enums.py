from django.db import models


class Permissions(models.IntegerChoices):
    FOR_ALL = 0, "Для всех"
    FOR_ONLINE_USERS = 1, "Для онлайн пользователей"
    FOR_OFFLINE_USERS = 2, "Для оффлайн пользователей"
    FOR_EMPLOYEES = 3, "Для работников"
