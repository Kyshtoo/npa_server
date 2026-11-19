from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name_ru = models.CharField(max_length=100, verbose_name="Название на русском")
    name_ky = models.CharField(
        max_length=100, blank=True, verbose_name="Название на кыргызском"
    )
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Показывать категорию")
    button_color = models.CharField(
        max_length=9,
        blank=True,
        default="",
        help_text="Цвет кнопки в формате #RRGGBB. Пустое поле — стандартный голубой.",
        verbose_name="Цвет кнопки",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_ru


class Document(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Действует"
        AMENDED = "amended", "Изменён"
        SUSPENDED = "suspended", "Приостановлен"
        REPEALED = "repealed", "Утратил силу"
        DRAFT = "draft", "Проект"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Категория",
    )
    title_ru = models.CharField(max_length=500, verbose_name="Название на русском")
    title_ky = models.CharField(
        max_length=500, blank=True, verbose_name="Название на кыргызском"
    )
    number = models.CharField(
        max_length=100, blank=True, verbose_name="Номер документа"
    )
    adoption_date = models.DateField(null=True, blank=True, verbose_name="Дата принятия")
    effective_date = models.DateField(
        null=True, blank=True, verbose_name="Дата вступления в силу"
    )
    place_ru = models.CharField(
        max_length=100, default="г. Бишкек", verbose_name="Место принятия на русском"
    )
    place_ky = models.CharField(
        max_length=100,
        blank=True,
        default="Бишкек ш.",
        verbose_name="Место принятия на кыргызском",
    )
    summary_ru = models.TextField(blank=True, verbose_name="Краткое описание на русском")
    summary_ky = models.TextField(blank=True, verbose_name="Краткое описание на кыргызском")
    content_ru = models.TextField(
        blank=True,
        help_text="Резервный текст, если структура ещё не заполнена.",
        verbose_name="Полный текст на русском",
    )
    content_ky = models.TextField(
        blank=True,
        help_text="Резервный текст, если структура ещё не заполнена.",
        verbose_name="Полный текст на кыргызском",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус",
    )
    source_url = models.URLField(blank=True, verbose_name="Официальный источник")
    revision = models.PositiveIntegerField(default=1, verbose_name="Номер редакции")
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        ordering = ["position", "-adoption_date", "id"]
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        indexes = [
            models.Index(
                fields=["category", "is_published", "position"],
                name="npa_doc_cat_pub_pos",
            ),
            models.Index(fields=["updated_at"], name="npa_doc_updated"),
        ]

    def __str__(self):
        return self.title_ru


class DocumentSection(models.Model):
    class SectionType(models.TextChoices):
        SECTION = "section", "Раздел"
        CHAPTER = "chapter", "Глава"
        ARTICLE = "article", "Статья"
        PART = "part", "Часть"
        ITEM = "item", "Пункт"
        SUBITEM = "subitem", "Подпункт"
        APPENDIX = "appendix", "Приложение"

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Документ",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительский элемент",
    )
    section_type = models.CharField(
        max_length=20,
        choices=SectionType.choices,
        default=SectionType.ARTICLE,
        verbose_name="Тип элемента",
    )
    number = models.CharField(max_length=50, blank=True, verbose_name="Номер")
    title_ru = models.CharField(
        max_length=500, blank=True, verbose_name="Заголовок на русском"
    )
    title_ky = models.CharField(
        max_length=500, blank=True, verbose_name="Заголовок на кыргызском"
    )
    content_ru = models.TextField(blank=True, verbose_name="Текст на русском")
    content_ky = models.TextField(blank=True, verbose_name="Текст на кыргызском")
    position = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Структурный элемент"
        verbose_name_plural = "Структура документа"
        indexes = [
            models.Index(
                fields=["document", "position"], name="npa_sec_doc_pos"
            ),
            models.Index(
                fields=["parent", "position"], name="npa_sec_parent_pos"
            ),
        ]

    def __str__(self):
        title = self.title_ru or self.title_ky or self.get_section_type_display()
        return f"{self.number} {title}".strip()

    def clean(self):
        super().clean()
        if self.parent_id:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError({"parent": "Элемент не может быть родителем самого себя."})
            if self.parent.document_id != self.document_id:
                raise ValidationError({"parent": "Родитель должен принадлежать тому же документу."})


class DocumentFile(models.Model):
    class Language(models.TextChoices):
        RU = "ru", "Русский"
        KY = "ky", "Кыргызский"

    class FileType(models.TextChoices):
        ORIGINAL = "original", "Официальный оригинал"
        APPENDIX = "appendix", "Приложение"
        OTHER = "other", "Другой файл"

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="files",
        verbose_name="Документ",
    )
    title = models.CharField(max_length=255, blank=True, verbose_name="Название файла")
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.RU,
        verbose_name="Язык",
    )
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.ORIGINAL,
        verbose_name="Тип файла",
    )
    file = models.FileField(upload_to="documents/%Y/%m/", verbose_name="PDF-файл")
    file_size = models.PositiveBigIntegerField(
        default=0, editable=False, verbose_name="Размер файла"
    )
    version = models.PositiveIntegerField(default=1, verbose_name="Версия файла")
    is_active = models.BooleanField(default=True, verbose_name="Актуальный файл")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        ordering = ["language", "file_type", "-version", "id"]
        verbose_name = "Файл документа"
        verbose_name_plural = "Файлы документа"
        indexes = [
            models.Index(
                fields=["document", "language", "is_active"],
                name="npa_file_doc_lang_act",
            )
        ]

    def __str__(self):
        return self.title or Path(self.file.name).name

    def save(self, *args, **kwargs):
        if self.file:
            try:
                self.file_size = self.file.size
            except (FileNotFoundError, OSError):
                pass
        super().save(*args, **kwargs)
