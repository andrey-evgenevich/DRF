from django.core.management.base import BaseCommand
from config.users.models import Payment, CustomUser
from config.lms.models import Course, Lesson

class Command(BaseCommand):
    help = 'Load sample payment data'

    def handle(self, *args, **options):
        user1 = CustomUser.objects.get(pk=1)
        user2 = CustomUser.objects.get(pk=2)
        course1 = Course.objects.get(pk=1)
        lesson3 = Lesson.objects.get(pk=3)

        Payment.objects.create(
            user=user1,
            paid_course=course1,
            amount=15000.00,
            payment_method='transfer'
        )

        Payment.objects.create(
            user=user2,
            paid_lesson=lesson3,
            amount=5000.00,
            payment_method='cash'
        )

        self.stdout.write(self.style.SUCCESS('Successfully loaded payment data'))