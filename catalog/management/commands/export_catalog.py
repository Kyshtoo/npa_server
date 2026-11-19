import json
from pathlib import Path

from django.core.management.base import BaseCommand

from catalog.services.catalog_export import build_catalog


class Command(BaseCommand):
    help = "Экспортирует опубликованный каталог в JSON для офлайн-сборки."

    def add_arguments(self, parser):
        parser.add_argument("output", type=Path)

    def handle(self, *args, **options):
        output = options["output"].resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(build_catalog(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.stdout.write(self.style.SUCCESS(f"Каталог сохранён: {output}"))
