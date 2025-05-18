from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def deactivate_inactive_users(self, months_inactive=6):
    """
    Деактивирует пользователей, не проявлявших активность более X месяцев
    :param months_inactive: количество месяцев неактивности для деактивации
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=months_inactive * 30)

        inactive_users = User.objects.filter(
            is_active=True,
            last_login__lt=cutoff_date
        )

        count = inactive_users.update(is_active=False)

        logger.info(f"Deactivated {count} inactive users (last login before {cutoff_date})")
        return f"Deactivated {count} inactive users"

    except Exception as e:
        logger.error(f"Error deactivating users: {e}")
        self.retry(exc=e, countdown=60)