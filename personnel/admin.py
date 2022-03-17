from django.contrib import admin

from utils.models_utils import ListDisplayAllModelFieldsAdminMixin

from .models import LocalPassport, Personnel, PersonnelDocument, Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass


class LocalPassportInline(admin.StackedInline):
    model = LocalPassport
    extra = 1


class PersonnelDocumentInline(admin.TabularInline):
    model = PersonnelDocument
    extra = 1


@admin.register(Personnel)
class PersonnelAdmin(ListDisplayAllModelFieldsAdminMixin, admin.ModelAdmin):
    inlines = [LocalPassportInline, PersonnelDocumentInline]
    filter_horizontal = ["workplaces"]
