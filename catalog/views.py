from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Document
from .serializers import (
    CategorySerializer,
    DocumentDetailSerializer,
    DocumentListSerializer,
)
from .services.catalog_export import build_catalog, build_manifest


def _published_documents():
    return (
        Document.objects.filter(
            is_published=True,
            category__is_active=True,
        )
        .select_related("category")
        .prefetch_related("files")
    )


def _apply_document_search(queryset, query, language):
    if not query:
        return queryset

    if language == "ky":
        search_filter = (
            Q(title_ky__icontains=query)
            | Q(summary_ky__icontains=query)
            | Q(content_ky__icontains=query)
            | Q(sections__title_ky__icontains=query)
            | Q(sections__content_ky__icontains=query)
            | Q(number__icontains=query)
        )
    else:
        search_filter = (
            Q(title_ru__icontains=query)
            | Q(summary_ru__icontains=query)
            | Q(content_ru__icontains=query)
            | Q(sections__title_ru__icontains=query)
            | Q(sections__content_ru__icontains=query)
            | Q(number__icontains=query)
        )

    return queryset.filter(search_filter).distinct()


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response(
        {
            "name": "NPA Catalog API",
            "schema_version": 2,
            "endpoints": {
                "categories": request.build_absolute_uri("categories/"),
                "search": request.build_absolute_uri("search/"),
                "manifest": request.build_absolute_uri("catalog/manifest/"),
                "catalog": request.build_absolute_uri("catalog/export/"),
            },
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    query = request.query_params.get("q", "").strip()
    language = request.query_params.get("lang", "ru")

    if query:
        field = "name_ky__icontains" if language == "ky" else "name_ru__icontains"
        categories = categories.filter(**{field: query})

    return Response(CategorySerializer(categories, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def category_document_list(request, category_id):
    category = get_object_or_404(Category, id=category_id, is_active=True)
    documents = _published_documents().filter(category=category)
    documents = _apply_document_search(
        documents,
        request.query_params.get("q", "").strip(),
        request.query_params.get("lang", "ru"),
    )
    serializer = DocumentListSerializer(
        documents,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def document_detail(request, document_id):
    document = get_object_or_404(
        _published_documents().prefetch_related("sections"),
        id=document_id,
    )
    serializer = DocumentDetailSerializer(
        document,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def search_documents(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response([])
    documents = _apply_document_search(
        _published_documents(),
        query,
        request.query_params.get("lang", "ru"),
    )
    serializer = DocumentListSerializer(
        documents,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def catalog_manifest(request):
    return Response(build_manifest(request=request))


@api_view(["GET"])
@permission_classes([AllowAny])
def catalog_export(request):
    return Response(build_catalog(request=request))
