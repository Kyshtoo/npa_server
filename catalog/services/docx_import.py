import re

from django.db import transaction
from docx import Document as DocxDocument

from catalog.models import Document, DocumentSection


_HEADING_PATTERNS = (
    (re.compile(r"^(?:РАЗДЕЛ|Раздел|БӨЛҮМ|Бөлүм)\s+([\w-]+)", re.UNICODE), "section", 0),
    (re.compile(r"^(?:ГЛАВА|Глава)\s+([\w-]+)", re.UNICODE), "chapter", 1),
    (re.compile(r"^(?:СТАТЬЯ|Статья|БЕРЕНЕ|Берене)\s+([\w-]+)", re.UNICODE), "article", 2),
    (re.compile(r"^(?:ЧАСТЬ|Часть|БӨЛҮК|Бөлүк)\s+([\w-]+)", re.UNICODE), "part", 3),
    (re.compile(r"^(\d+(?:\.\d+){2,})[.)]?\s+", re.UNICODE), "subitem", 5),
    (re.compile(r"^(\d+(?:\.\d+)*)[.)]\s+", re.UNICODE), "item", 4),
    (re.compile(r"^(?:ПРИЛОЖЕНИЕ|Приложение|ТИРКЕМЕ|Тиркеме)\s*([\w-]*)", re.UNICODE), "appendix", 0),
)


def _heading_info(text):
    for pattern, section_type, rank in _HEADING_PATTERNS:
        match = pattern.match(text)
        if match:
            return section_type, rank, (match.group(1) or "")
    return None


@transaction.atomic
def import_docx(
    uploaded_file,
    *,
    category,
    language,
    title,
    number="",
    adoption_date=None,
    publish=False,
):
    """Create a document and a first-pass structure from a Word file.

    The importer deliberately stays conservative: headings are recognised by
    their visible text, while every unrecognised paragraph is preserved as body
    text. An editor can correct the generated hierarchy before publishing.
    """

    source = DocxDocument(uploaded_file)
    paragraphs = [paragraph.text.strip() for paragraph in source.paragraphs]
    paragraphs = [paragraph for paragraph in paragraphs if paragraph]

    document_values = {
        "category": category,
        "number": number,
        "adoption_date": adoption_date,
        "is_published": publish,
        "status": Document.Status.ACTIVE if publish else Document.Status.DRAFT,
    }
    if language == "ky":
        document_values.update(title_ru=title, title_ky=title)
    else:
        document_values.update(title_ru=title)

    document = Document.objects.create(**document_values)
    content_field = "content_ky" if language == "ky" else "content_ru"
    title_field = "title_ky" if language == "ky" else "title_ru"
    setattr(document, content_field, "\n\n".join(paragraphs))
    document.save(update_fields=[content_field, "updated_at"])

    stack = {}
    current_section = None
    current_content = []
    position = 0

    def flush_content():
        nonlocal current_content
        if current_section is not None and current_content:
            setattr(current_section, content_field, "\n\n".join(current_content))
            current_section.save(update_fields=[content_field, "updated_at"])
        current_content = []

    for paragraph in paragraphs:
        heading = _heading_info(paragraph)
        if heading is None:
            current_content.append(paragraph)
            continue

        flush_content()
        section_type, rank, number_value = heading
        parent = None
        for candidate_rank in range(rank - 1, -1, -1):
            if candidate_rank in stack:
                parent = stack[candidate_rank]
                break

        values = {
            "document": document,
            "parent": parent,
            "section_type": section_type,
            "number": number_value,
            "position": position,
            title_field: paragraph,
        }
        current_section = DocumentSection.objects.create(**values)
        stack[rank] = current_section
        for obsolete_rank in [value for value in stack if value > rank]:
            del stack[obsolete_rank]
        position += 1

    flush_content()

    if not document.sections.exists():
        fallback = {
            "document": document,
            "section_type": DocumentSection.SectionType.ARTICLE,
            "position": 0,
            title_field: "Текст документа" if language == "ru" else "Документтин тексти",
            content_field: "\n\n".join(paragraphs),
        }
        DocumentSection.objects.create(**fallback)

    return document
