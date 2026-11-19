from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Category, Document


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name_ru",
        "name_ky",
        "position",
        "is_active",
    )
    list_editable = (
        "position",
        "is_active",
    )
    search_fields = (
        "name_ru",
        "name_ky",
    )
    ordering = (
        "position",
        "id",
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_ru",
        "category",
        "number",
        "adoption_date",
        "position",
        "is_published",
    )
    list_filter = (
        "category",
        "is_published",
        "adoption_date",
    )
    list_editable = (
        "position",
        "is_published",
    )
    search_fields = (
        "title_ru",
        "title_ky",
        "number",
        "content_ru",
        "content_ky",
    )
    ordering = (
        "position",
        "-adoption_date",
        "id",
    )
    