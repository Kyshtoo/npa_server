import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_document"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="button_color",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Цвет кнопки в формате #RRGGBB. Пустое поле — стандартный голубой.",
                max_length=9,
                verbose_name="Цвет кнопки",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name="Дата изменения",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="document",
            name="effective_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="Дата вступления в силу"
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="revision",
            field=models.PositiveIntegerField(default=1, verbose_name="Номер редакции"),
        ),
        migrations.AddField(
            model_name="document",
            name="source_url",
            field=models.URLField(blank=True, verbose_name="Официальный источник"),
        ),
        migrations.AddField(
            model_name="document",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Действует"),
                    ("amended", "Изменён"),
                    ("suspended", "Приостановлен"),
                    ("repealed", "Утратил силу"),
                    ("draft", "Проект"),
                ],
                default="active",
                max_length=20,
                verbose_name="Статус",
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="summary_ky",
            field=models.TextField(blank=True, verbose_name="Краткое описание на кыргызском"),
        ),
        migrations.AddField(
            model_name="document",
            name="summary_ru",
            field=models.TextField(blank=True, verbose_name="Краткое описание на русском"),
        ),
        migrations.AlterField(
            model_name="document",
            name="content_ru",
            field=models.TextField(
                blank=True,
                help_text="Резервный текст, если структура ещё не заполнена.",
                verbose_name="Полный текст на русском",
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="content_ky",
            field=models.TextField(
                blank=True,
                help_text="Резервный текст, если структура ещё не заполнена.",
                verbose_name="Полный текст на кыргызском",
            ),
        ),
        migrations.CreateModel(
            name="DocumentSection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "section_type",
                    models.CharField(
                        choices=[
                            ("section", "Раздел"),
                            ("chapter", "Глава"),
                            ("article", "Статья"),
                            ("part", "Часть"),
                            ("item", "Пункт"),
                            ("subitem", "Подпункт"),
                            ("appendix", "Приложение"),
                        ],
                        default="article",
                        max_length=20,
                        verbose_name="Тип элемента",
                    ),
                ),
                ("number", models.CharField(blank=True, max_length=50, verbose_name="Номер")),
                (
                    "title_ru",
                    models.CharField(blank=True, max_length=500, verbose_name="Заголовок на русском"),
                ),
                (
                    "title_ky",
                    models.CharField(blank=True, max_length=500, verbose_name="Заголовок на кыргызском"),
                ),
                ("content_ru", models.TextField(blank=True, verbose_name="Текст на русском")),
                ("content_ky", models.TextField(blank=True, verbose_name="Текст на кыргызском")),
                ("position", models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата изменения")),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sections",
                        to="catalog.document",
                        verbose_name="Документ",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="catalog.documentsection",
                        verbose_name="Родительский элемент",
                    ),
                ),
            ],
            options={
                "verbose_name": "Структурный элемент",
                "verbose_name_plural": "Структура документа",
                "ordering": ["position", "id"],
                "indexes": [
                    models.Index(fields=["document", "position"], name="npa_sec_doc_pos"),
                    models.Index(fields=["parent", "position"], name="npa_sec_parent_pos"),
                ],
            },
        ),
        migrations.CreateModel(
            name="DocumentFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=255, verbose_name="Название файла")),
                (
                    "language",
                    models.CharField(
                        choices=[("ru", "Русский"), ("ky", "Кыргызский")],
                        default="ru",
                        max_length=2,
                        verbose_name="Язык",
                    ),
                ),
                (
                    "file_type",
                    models.CharField(
                        choices=[
                            ("original", "Официальный оригинал"),
                            ("appendix", "Приложение"),
                            ("other", "Другой файл"),
                        ],
                        default="original",
                        max_length=20,
                        verbose_name="Тип файла",
                    ),
                ),
                ("file", models.FileField(upload_to="documents/%Y/%m/", verbose_name="PDF-файл")),
                (
                    "file_size",
                    models.PositiveBigIntegerField(default=0, editable=False, verbose_name="Размер файла"),
                ),
                ("version", models.PositiveIntegerField(default=1, verbose_name="Версия файла")),
                ("is_active", models.BooleanField(default=True, verbose_name="Актуальный файл")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата изменения")),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to="catalog.document",
                        verbose_name="Документ",
                    ),
                ),
            ],
            options={
                "verbose_name": "Файл документа",
                "verbose_name_plural": "Файлы документа",
                "ordering": ["language", "file_type", "-version", "id"],
                "indexes": [
                    models.Index(
                        fields=["document", "language", "is_active"],
                        name="npa_file_doc_lang_act",
                    )
                ],
            },
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["category", "is_published", "position"],
                name="npa_doc_cat_pub_pos",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["updated_at"], name="npa_doc_updated"),
        ),
    ]
