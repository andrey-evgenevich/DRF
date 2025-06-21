from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from users.models import CustomUser


@shared_task
def user_block():
    users = CustomUser.objects.filter(
        last_login__lt=now() - timedelta(days=30)
    )
    if users.count() > 0:
        users.update(is_active=False)
        users.save()
