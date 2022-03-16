from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group as BaseGroup

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import GeneratedPassword, Group, RefreshToken


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "uuid", "date")
    search_fields = ("user",)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "surname",
        "name",
        "fathers_name",
        "email",
        "phone_number",
        "date_of_birth",
        "date_joined",
    )
    readonly_fields = ("date_joined",)
    search_fields = ("name", "surname", "email", "phone_number")
    list_filter = ("is_staff", "is_superuser", "is_active")
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "surname",
                    "name",
                    "fathers_name",
                    "email",
                    "phone_number",
                    "date_of_birth",
                    "date_joined",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )


@admin.register(GeneratedPassword)
class GeneratedPasswordAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    pass


admin.site.unregister(BaseGroup)
admin.site.register(Group, GroupAdmin)
admin.site.register(get_user_model(), UserAdmin)
