from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт или обновляет группу редакторов каталога НПА."

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="Редакторы НПА")
        permissions = Permission.objects.filter(
            content_type__app_label="catalog",
            codename__in=(
                "view_category",
                "add_category",
                "change_category",
                "view_document",
                "add_document",
                "change_document",
                "view_documentsection",
                "add_documentsection",
                "change_documentsection",
                "delete_documentsection",
                "view_documentfile",
                "add_documentfile",
                "change_documentfile",
                "delete_documentfile",
            ),
        )
        group.permissions.set(permissions)
        self.stdout.write(
            self.style.SUCCESS(
                f"Группа «{group.name}» настроена. Выдано прав: {permissions.count()}."
            )
        )
