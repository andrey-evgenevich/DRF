from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from config.lms.models import Course, Lesson


class Command(BaseCommand):
    help = "Creates moderator group with permissions"

    def handle(self, *args, **options):
        # Создаем группу
        mod_group, created = Group.objects.get_or_create(name="moderators")

        # Получаем разрешения
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        permissions = Permission.objects.filter(
            content_type__in=[course_content_type, lesson_content_type],
            codename__in=[
                "change_course",
                "view_course",
                "change_lesson",
                "view_lesson",
            ],
        )

        # Добавляем разрешения в группу
        mod_group.permissions.set(permissions)
        mod_group.save()

        self.stdout.write(self.style.SUCCESS("Successfully created moderators group"))
