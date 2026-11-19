from django.db import models

# Create your models here.

class Category(models.Model):
    name_ru = models.CharField(
        max_length=100,
        verbose_name="Название на русском",
    )
    name_ky = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Название на кыргызском",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Показывать категорию",
    )

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name_ru

class Document(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name="Категория",
    )
    title_ru = models.CharField(
        max_length=500,
        verbose_name="Название на русском",
    )
    title_ky = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Название на кыргызском",
    )
    number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Номер документа",
    )
    adoption_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата принятия",
    )
    place_ru = models.CharField(
        max_length=100,
        default="г. Бишкек",
        verbose_name="Место принятия на русском",
    )
    place_ky = models.CharField(
        max_length=100,
        blank=True,
        default="Бишкек ш.",
        verbose_name="Место принятия на кыргызском",
    )
    content_ru = models.TextField(
        blank=True,
        verbose_name="Текст на русском",
    )
    content_ky = models.TextField(
        blank=True,
        verbose_name="Текст на кыргызском",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Опубликован",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения",
    )

    class Meta:
        ordering = ["position", "-adoption_date", "id"]
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title_ru