from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# Create your views here.

from .models import Category, Document
from .serializers import (
    CategorySerializer,
    DocumentListSerializer,
    DocumentDetailSerializer,
)


@api_view(["GET"])
def category_list(request):
	categories = Category.objects.filter(is_active=True)
	serializers = CategorySerializer(categories, many=True)
	return Response(serializers.data)

@api_view(["GET"])
def category_document_list(request, category_id):
    category = get_object_or_404(
        Category,
        id=category_id,
        is_active=True,
    )

    documents = Document.objects.filter(
        category=category,
        is_published=True, 
    )

    serializer = DocumentListSerializer(
        documents,
        many=True,
    )

    return Response(serializer.data)

@api_view(["GET"])
def document_detail(request, document_id):
    document = get_object_or_404(
        Document,
        id=document_id,
        is_published=True,
        category__is_active=True,
    )

    serializer = DocumentDetailSerializer(document)
    return Response(serializer.data)