from rest_framework import serializers

from .models import Category, Document, DocumentFile, DocumentSection


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name_ru",
            "name_ky",
            "position",
            "button_color",
        )


class DocumentFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFile
        fields = (
            "id",
            "document_id",
            "title",
            "language",
            "file_type",
            "url",
            "file_size",
            "version",
            "uploaded_at",
        )

    def get_url(self, obj):
        if not obj.file:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class DocumentSectionSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(read_only=True)
    document_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = DocumentSection
        fields = (
            "id",
            "document_id",
            "parent_id",
            "section_type",
            "number",
            "title_ru",
            "title_ky",
            "content_ru",
            "content_ky",
            "position",
        )


class DocumentListSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(read_only=True)
    has_pdf = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "category_id",
            "title_ru",
            "title_ky",
            "number",
            "adoption_date",
            "effective_date",
            "place_ru",
            "place_ky",
            "summary_ru",
            "summary_ky",
            "status",
            "revision",
            "updated_at",
            "has_pdf",
        )

    def get_has_pdf(self, obj):
        return obj.files.filter(is_active=True).exists()


class DocumentDetailSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(read_only=True)
    sections = DocumentSectionSerializer(many=True, read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = (
            "id",
            "category_id",
            "title_ru",
            "title_ky",
            "number",
            "adoption_date",
            "effective_date",
            "place_ru",
            "place_ky",
            "summary_ru",
            "summary_ky",
            "content_ru",
            "content_ky",
            "status",
            "source_url",
            "revision",
            "updated_at",
            "sections",
            "files",
        )

    def get_files(self, obj):
        files = obj.files.filter(is_active=True)
        return DocumentFileSerializer(
            files,
            many=True,
            context=self.context,
        ).data
