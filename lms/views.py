from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from rest_framework import viewsets, status
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from config.users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from .models import Subscription
from .serializers import SubscriptionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .paginators import CoursePaginator, LessonPaginator
from django.urls import reverse
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsAdminUser | IsOwner]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    Subscription.objects.filter(
                        user=self.request.user, course=OuterRef("pk")
                    )
                )
            )
        return queryset

    def perform_update(self, serializer):
        instance = serializer.save()

        # Отправляем уведомления подписчикам асинхронно
        if self.is_course_updated(instance, serializer):
            send_course_update_notification.delay(instance.id)

        return instance

    def is_course_updated(self, instance, serializer):
        """Проверяем, были ли обновлены значимые поля"""
        old_data = serializer.instance.__dict__
        new_data = serializer.validated_data

        significant_fields = ["title", "description", "lessons"]
        return any(
            field in new_data and new_data[field] != old_data.get(field)
            for field in significant_fields
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Отдельное действие для публикации курса"""
        course = self.get_object()
        course.is_published = True
        course.save()

        # Отправляем уведомления при публикации
        send_course_update_notification.delay(course.id)

        return Response({"status": "курс опубликован"})


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsAdminUser | IsOwner]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (
            self.request.user.is_staff
            or self.request.user.groups.filter(name="moderators").exists()
        ):
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def subscribe(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = Subscription.objects.get_or_create(
            user=request.user, course_id=course_id
        )

        if created:
            return Response(
                {"status": "подписка создана"}, status=status.HTTP_201_CREATED
            )
        return Response({"status": "вы уже подписаны"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def unsubscribe(self, request):
        course_id = request.data.get("course_id")
        if not course_id:
            return Response(
                {"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        deleted, _ = Subscription.objects.filter(
            user=request.user, course_id=course_id
        ).delete()

        if deleted:
            return Response({"status": "подписка удалена"}, status=status.HTTP_200_OK)
        return Response(
            {"status": "подписка не найдена"}, status=status.HTTP_404_NOT_FOUND
        )
