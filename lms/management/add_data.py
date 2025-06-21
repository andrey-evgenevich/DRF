from django.core.management import call_command
from django.core.management.base import BaseCommand

from lms.models import Course, Lesson
from users.models import Payment, CustomUser


class Command(BaseCommand):
    help = "Добавление данных из фикстур"

    def handle(self, *args, **kwargs):

        Course.objects.all().delete()
        Lesson.objects.all().delete()
        CustomUser.objects.all().delete()
        Payment.objects.all().delete()

        call_command("loaddata", "course_fixture.json", format="json")
        self.stdout.write(self.style.SUCCESS("Курсы загружены из фикстур успешно"))
        call_command("loaddata", "lesson_fixture.json", format="json")
        self.stdout.write(self.style.SUCCESS("Уроки загружены из фикстур успешно"))
        call_command("loaddata", "users_fixture.json", format="json")
        self.stdout.write(self.style.SUCCESS("Уроки загружены из фикстур успешно"))
        call_command("loaddata", "payment_fixture.json", format="json")
        self.stdout.write(self.style.SUCCESS("Уроки загружены из фикстур успешно"))
