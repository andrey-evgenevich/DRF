from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .validators import validate_no_external_links
from config.users.models import CustomUser


class Course(models.Model):
    title = models.CharField(_("title"), max_length=255)
    preview = models.ImageField(_("preview image"), upload_to="courses/previews/")
    description = models.TextField(
        _("description"), validators=[validate_no_external_links], blank=True, null=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )
    video_link = models.URLField(
        verbose_name="Ссылка на видео",
        validators=[validate_no_external_links],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name=_("course"),
    )
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(
        _("description"), validators=[validate_no_external_links], blank=True, null=True
    )
    preview = models.ImageField(_("preview image"), upload_to="lessons/previews/")
    video_link = models.URLField(_("video link"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = _("lesson")
        verbose_name_plural = _("lessons")

    def __str__(self):
        return self.title


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата подписки"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ["user", "course"]  # Одна подписка на пользователя+курс

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"
