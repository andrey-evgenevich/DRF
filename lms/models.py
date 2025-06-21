from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название курса")
    price = models.PositiveIntegerField(default=100, verbose_name="Цена в долларах")
    preview = models.ImageField(
        upload_to="course", blank=True, null=True, verbose_name="Картинка курса"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название урока")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    preview = models.ImageField(
        upload_to="lesson", blank=True, null=True, verbose_name="Картинка урока"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="lessons",
        verbose_name="Курс",
    )
    url = models.URLField(max_length=300, verbose_name="Ссылка на видео")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class CourseSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="user_course_subscription",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="course_subscription",
    )

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписка на курсы"


class CoursePayment(models.Model):
    """Модель для оплаты курсов"""

    amount = models.PositiveIntegerField(verbose_name="сумма оплаты")
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="id сессии"
    )
    link = models.URLField(
        max_length=400, blank=True, null=True, verbose_name="ссылка на оплату"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="user_payments",
        verbose_name="пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="course_payment",
        verbose_name="Курс",
    )

    def __str__(self):
        return self.amount

    class Meta:
        verbose_name = "Оплата за курс"
        verbose_name_plural = "Оплата за курсы"
