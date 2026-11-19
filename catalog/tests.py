from io import BytesIO

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from docx import Document as DocxDocument
from rest_framework.test import APIClient

from .models import Category, Document, DocumentSection
from .services.docx_import import import_docx


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name_ru="Законы",
            name_ky="Мыйзамдар",
            position=1,
            button_color="#FFC205",
        )
        self.document = Document.objects.create(
            category=self.category,
            title_ru="Закон о недрах",
            title_ky="Жер казынасы жөнүндө мыйзам",
            number="49",
            content_ru="Резервный текст",
            is_published=True,
        )
        self.section = DocumentSection.objects.create(
            document=self.document,
            section_type=DocumentSection.SectionType.ARTICLE,
            number="1",
            title_ru="Статья 1. Общие положения",
            title_ky="1-берене. Жалпы жоболор",
            content_ru="Правила недропользования",
            content_ky="Жер казынасын пайдалануу эрежелери",
            position=1,
        )
        Document.objects.create(
            category=self.category,
            title_ru="Неопубликованный черновик",
            is_published=False,
        )

    def test_public_lists_hide_drafts(self):
        response = self.client.get(
            reverse("category-document-list", args=(self.category.pk,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.document.pk)

    def test_detail_contains_structure(self):
        response = self.client.get(reverse("document-detail", args=(self.document.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sections"][0]["id"], self.section.pk)

    def test_search_uses_selected_language(self):
        response = self.client.get(
            reverse("document-search"),
            {"q": "эрежелери", "lang": "ky"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], [self.document.pk])

    def test_export_is_offline_ready(self):
        response = self.client.get(reverse("catalog-export"))
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["schema_version"], 2)
        self.assertEqual(len(payload["documents"]), 1)
        self.assertEqual(len(payload["sections"]), 1)
        self.assertIn("revision", payload)

    def test_manifest_reports_download_size(self):
        response = self.client.get(reverse("catalog-manifest"))
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(payload["size_bytes"], 0)
        self.assertEqual(payload["documents_count"], 1)


class DocxImportTests(TestCase):
    def test_import_creates_editable_hierarchy(self):
        category = Category.objects.create(name_ru="Законы")
        source = DocxDocument()
        source.add_paragraph("Раздел I. Общие положения")
        source.add_paragraph("Глава 1. Основы")
        source.add_paragraph("Статья 1. Предмет регулирования")
        source.add_paragraph("Содержимое первой статьи.")
        buffer = BytesIO()
        source.save(buffer)
        uploaded = SimpleUploadedFile(
            "law.docx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        document = import_docx(
            uploaded,
            category=category,
            language="ru",
            title="Тестовый закон",
        )

        self.assertFalse(document.is_published)
        self.assertEqual(document.status, Document.Status.DRAFT)
        self.assertEqual(document.sections.count(), 3)
        article = document.sections.get(section_type=DocumentSection.SectionType.ARTICLE)
        self.assertEqual(article.content_ru, "Содержимое первой статьи.")
        self.assertIsNotNone(article.parent)


class RoleSetupTests(TestCase):
    def test_editor_group_is_created(self):
        call_command("setup_roles")
        group = Group.objects.get(name="Редакторы НПА")
        self.assertTrue(group.permissions.filter(codename="change_document").exists())
        self.assertFalse(group.permissions.filter(codename="delete_document").exists())
