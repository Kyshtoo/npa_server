from django import forms

from .models import Category, DocumentFile


class DocxImportForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        label="Категория",
    )
    language = forms.ChoiceField(
        choices=DocumentFile.Language.choices,
        label="Язык документа",
    )
    title = forms.CharField(max_length=500, label="Название документа")
    number = forms.CharField(max_length=100, required=False, label="Номер")
    adoption_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Дата принятия",
    )
    file = forms.FileField(
        label="Файл Word (.docx)",
        help_text="Импорт создаёт черновую структуру. Проверьте её перед публикацией.",
    )
    publish = forms.BooleanField(
        required=False,
        initial=False,
        label="Опубликовать сразу",
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.lower().endswith(".docx"):
            raise forms.ValidationError("Поддерживаются только файлы .docx.")
        if uploaded_file.size > 20 * 1024 * 1024:
            raise forms.ValidationError("Размер файла не должен превышать 20 МБ.")
        return uploaded_file
