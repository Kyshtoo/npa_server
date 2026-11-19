from django.urls import path

from .views import category_list, category_document_list, document_detail


urlpatterns = [
    path("categories/", 
        category_list, 
        name="category-list"),
    path(
        "categories/<int:category_id>/documents/",
        category_document_list,
        name="category-document-list",
    ),
    path(
        "documents/<int:document_id>/",
        document_detail,
        name="document-detail",
    ),
]