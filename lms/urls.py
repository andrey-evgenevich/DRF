from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonCreateApiView,
    LessonListApiView,
    LessonUpdateApiView,
    LessonDestroyApiView,
    LessonRetrieveApiView,
    CourseSubscriptionApiView,
    CoursePaymentCreateApiView,
)

app_name = "lms"

router = DefaultRouter()
router.register(r"course", CourseViewSet, basename="course")

urlpatterns = [
    path("lesson/", LessonListApiView.as_view(), name="lesson_list"),
    path("lesson/<int:pk>", LessonRetrieveApiView.as_view(), name="lesson_retrieve"),
    path("lesson/create", LessonCreateApiView.as_view(), name="lesson_create"),
    path("lesson/<int:pk>/update", LessonUpdateApiView.as_view(), name="lesson_update"),
    path(
        "lesson/<int:pk>/delete", LessonDestroyApiView.as_view(), name="lesson_delete"
    ),
    path(
        "course/subscribe", CourseSubscriptionApiView.as_view(), name="course_subscribe"
    ),
    path("payment/", CoursePaymentCreateApiView.as_view(), name="payment"),
] + router.urls
