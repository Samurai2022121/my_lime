from django.contrib import admin

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import RefreshToken


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'uuid', 'date')
    search_fields = ('user', )


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'fathers_name', 'email', 'phone_number', 'date_of_birth', 'date_joined')
    readonly_fields = ('date_joined',)
    search_fields = ('name', 'surname', 'email', 'phone_number')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('surname', 'name', 'fathers_name', 'email', 'phone_number',
                           'date_of_birth', 'date_joined')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )


admin.site.unregister(Group)
admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)
