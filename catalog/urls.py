from django.urls import path

from .views import (
    api_root,
    catalog_export,
    catalog_manifest,
    category_document_list,
    category_list,
    document_detail,
    search_documents,
)


urlpatterns = [
    path("", api_root, name="api-root"),
    path("categories/", category_list, name="category-list"),
    path(
        "categories/<int:category_id>/documents/",
        category_document_list,
        name="category-document-list",
    ),
    path("documents/<int:document_id>/", document_detail, name="document-detail"),
    path("search/", search_documents, name="document-search"),
    path("catalog/manifest/", catalog_manifest, name="catalog-manifest"),
    path("catalog/export/", catalog_export, name="catalog-export"),
]
