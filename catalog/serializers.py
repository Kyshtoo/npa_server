from rest_framework import serializers

from .models import Category, Document

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = (
			"id",
			"name_ru",
			"name_ky",
			"position",
			)

class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "id",
            "title_ru",
            "title_ky",
            "number",
            "adoption_date",
            "place_ru",
            "place_ky",
        )

class DocumentDetailSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = (
            "id",
            "category_id",
            "title_ru",
            "title_ky",
            "number",
            "adoption_date",
            "place_ru",
            "place_ky",
            "content_ru",
            "content_ky",
        )