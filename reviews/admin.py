from django.contrib import admin

from .models import Star


@admin.register(Star)
class SectionAdmin(admin.ModelAdmin):
    list_filter = ("user",)
