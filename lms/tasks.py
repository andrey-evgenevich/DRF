from celery import shared_task
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from lms.models import Course
from config.settings import DEFAULT_FROM_EMAIL


@shared_task
def send_mail_update_course(course_id):
    """Отправка подписчикам уведомлений об изменениях в курсе"""
    course = get_object_or_404(Course, id=course_id)
    subscriptions = course.course_subscription.all()
    recipient_list = [sub.user.email for sub in subscriptions]
    subject = f"Курс {course.name} обновлен!"
    message = f'Здравствуйте! Сообщаем, что в курсе "{course.name}" обновления!'

    from_email = DEFAULT_FROM_EMAIL

    # Отправка письма
    responses = {}

    for recipient in recipient_list:
        try:
            send_mail(subject, message, from_email, [recipient])

            responses[recipient] = "Успешно отправлено"
        except Exception as e:
            responses[recipient] = f"Ошибка: {str(e)}"

    print(responses)
