from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone

from .forms import DocxImportForm
from .models import Category, Document, DocumentFile, DocumentSection
from .services.docx_import import import_docx


admin.site.site_header = "НПА Кыргызской геологической службы"
admin.site.site_title = "Администрирование НПА"
admin.site.index_title = "Управление каталогом"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name_ru",
        "name_ky",
        "position",
        "button_color",
        "is_active",
    )
    list_editable = ("position", "button_color", "is_active")
    search_fields = ("name_ru", "name_ky")
    ordering = ("position", "id")


class DocumentFileInline(admin.TabularInline):
    model = DocumentFile
    extra = 0
    fields = (
        "title",
        "language",
        "file_type",
        "file",
        "version",
        "is_active",
        "file_size",
    )
    readonly_fields = ("file_size",)


@admin.action(description="Опубликовать выбранные документы")
def publish_documents(modeladmin, request, queryset):
    count = queryset.update(is_published=True, updated_at=timezone.now())
    modeladmin.message_user(request, f"Опубликовано документов: {count}.")


@admin.action(description="Снять выбранные документы с публикации")
def unpublish_documents(modeladmin, request, queryset):
    count = queryset.update(is_published=False, updated_at=timezone.now())
    modeladmin.message_user(request, f"Снято с публикации: {count}.")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    change_list_template = "admin/catalog/document/change_list.html"

    # КНОПКИ СОХРАНЕНИЯ:
    # True добавляет такой же блок «Сохранить» сверху страницы документа.
    save_on_top = True

    list_display = (
        "id",
        "title_ru",
        "category",
        "number",
        "status",
        "revision",
        "adoption_date",
        "position",
        "is_published",
        "updated_at",
    )
    list_filter = ("category", "status", "is_published", "adoption_date")
    list_editable = ("position", "is_published")
    search_fields = (
        "title_ru",
        "title_ky",
        "number",
        "content_ru",
        "content_ky",
        "sections__title_ru",
        "sections__title_ky",
        "sections__content_ru",
        "sections__content_ky",
    )
    ordering = ("position", "-adoption_date", "id")
    readonly_fields = ("created_at", "updated_at")
    # Структура большого закона намеренно не выводится встроенными формами:
    # сотни разделов перегружали страницу и JavaScript Django Admin.
    # Сами разделы не удаляются и доступны отдельно в «Структуре документа».
    inlines = (DocumentFileInline,)
    actions = (publish_documents, unpublish_documents)
    fieldsets = (
        (
            "Основные сведения",
            {
                "fields": (
                    "category",
                    "title_ru",
                    "title_ky",
                    "number",
                    "adoption_date",
                    "effective_date",
                    "place_ru",
                    "place_ky",
                    "status",
                    "source_url",
                    "revision",
                )
            },
        ),
        (
            "Краткое описание",
            {"fields": ("summary_ru", "summary_ky")},
        ),
        (
            "Резервный полный текст",
            {
                "classes": ("collapse",),
                "fields": ("content_ru", "content_ky"),
            },
        ),
        (
            "Публикация",
            {
                "fields": (
                    "position",
                    "is_published",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_urls(self):
        custom_urls = [
            path(
                "import-docx/",
                self.admin_site.admin_view(self.import_docx_view),
                name="catalog_document_import_docx",
            )
        ]
        return custom_urls + super().get_urls()

    def import_docx_view(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied

        form = DocxImportForm(request.POST or None, request.FILES or None)
        if request.method == "POST" and form.is_valid():
            document = import_docx(
                form.cleaned_data["file"],
                category=form.cleaned_data["category"],
                language=form.cleaned_data["language"],
                title=form.cleaned_data["title"],
                number=form.cleaned_data["number"],
                adoption_date=form.cleaned_data["adoption_date"],
                publish=form.cleaned_data["publish"],
            )
            messages.success(
                request,
                "Документ импортирован. Проверьте заголовки, вложенность и текст.",
            )
            return redirect(
                reverse("admin:catalog_document_change", args=(document.pk,))
            )

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "form": form,
            "title": "Импорт документа из Word",
        }
        return render(request, "admin/catalog/document/import_docx.html", context)


@admin.register(DocumentSection)
class DocumentSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "section_type",
        "number",
        "title_ru",
        "parent",
        "position",
    )
    list_filter = ("section_type", "document__category")
    search_fields = (
        "document__title_ru",
        "title_ru",
        "title_ky",
        "content_ru",
        "content_ky",
    )
    ordering = ("document", "position", "id")


@admin.register(DocumentFile)
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document",
        "language",
        "file_type",
        "version",
        "file_size",
        "is_active",
        "uploaded_at",
    )
    list_filter = ("language", "file_type", "is_active")
    search_fields = ("document__title_ru", "document__title_ky", "title")
    readonly_fields = ("file_size", "uploaded_at", "updated_at")
