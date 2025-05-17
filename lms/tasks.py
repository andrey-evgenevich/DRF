from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Subscription
import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_course_update_notification(self, course_id):
    try:
        course_subscriptions = Subscription.objects.filter(
            course_id=course_id
        ).select_related('user', 'course')

        if not course_subscriptions.exists():
            logger.info(f"No subscribers for course {course_id}")
            return

        for subscription in course_subscriptions:
            try:
                subject = f"Обновление курса: {subscription.course.title}"
                message = render_to_string('emails/course_update.html', {
                    'course': subscription.course,
                    'user': subscription.user
                })

                send_mail(
                    subject=subject,
                    message='',  # Текстовая версия (пустая, так как используем html_message)
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscription.user.email],
                    html_message=message,
                    fail_silently=False
                )
                logger.info(f"Sent update to {subscription.user.email}")

            except Exception as e:
                logger.error(f"Error sending to {subscription.user.email}: {e}")
                continue

        return f"Sent updates to {course_subscriptions.count()} subscribers"

    except Exception as e:
        logger.error(f"Error processing course update: {e}")
        self.retry(countdown=60, exc=e)


@shared_task
def deactivate_inactive_users():
    """
    Деактивирует пользователей, которые не заходили более месяца
    """
    try:
        month_ago = timezone.now() - timedelta(days=30)

        inactive_users = User.objects.filter(
            last_login__lt=month_ago,
            is_active=True
        )

        count = inactive_users.update(is_active=False)

        logger.info(f"Deactivated {count} inactive users")
        return f"Deactivated {count} inactive users"

    except Exception as e:
        logger.error(f"Error deactivating users: {e}")
        raise