import json

from django.db.models import Max
from django.utils import timezone

from catalog.models import Category, Document, DocumentFile, DocumentSection
from catalog.serializers import (
    CategorySerializer,
    DocumentDetailSerializer,
)


SCHEMA_VERSION = 2


def _latest_revision():
    candidates = [
        Category.objects.filter(is_active=True).aggregate(value=Max("updated_at"))["value"],
        Document.objects.filter(is_published=True).aggregate(value=Max("updated_at"))["value"],
        DocumentSection.objects.filter(document__is_published=True).aggregate(
            value=Max("updated_at")
        )["value"],
        DocumentFile.objects.filter(
            document__is_published=True,
            is_active=True,
        ).aggregate(value=Max("updated_at"))["value"],
    ]
    latest = max((value for value in candidates if value is not None), default=None)
    return latest.isoformat() if latest else "0"


def build_catalog(request=None):
    categories = Category.objects.filter(is_active=True)
    documents = (
        Document.objects.filter(
            is_published=True,
            category__is_active=True,
        )
        .select_related("category")
        .prefetch_related("sections", "files")
    )

    document_values = []
    section_values = []
    file_values = []

    for document in documents:
        value = dict(
            DocumentDetailSerializer(
                document,
                context={"request": request},
            ).data
        )
        section_values.extend(value.pop("sections", []))
        file_values.extend(value.pop("files", []))
        document_values.append(value)

    return {
        "schema_version": SCHEMA_VERSION,
        "revision": _latest_revision(),
        "generated_at": timezone.now().isoformat(),
        "categories": CategorySerializer(categories, many=True).data,
        "documents": document_values,
        "sections": section_values,
        "files": file_values,
    }


def build_manifest(request=None):
    catalog = build_catalog(request=request)
    encoded = json.dumps(catalog, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )
    return {
        "schema_version": catalog["schema_version"],
        "revision": catalog["revision"],
        "generated_at": catalog["generated_at"],
        "size_bytes": len(encoded),
        "categories_count": len(catalog["categories"]),
        "documents_count": len(catalog["documents"]),
    }
