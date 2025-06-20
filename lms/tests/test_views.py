from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from config.users.models import CustomUser
from config.lms.models import Course, Lesson, Subscription


class LessonCRUDTests(APITestCase):
    def setUp(self):
        # Создаем тестовых пользователей
        self.admin = CustomUser.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.moderator = CustomUser.objects.create_user(
            email="moderator@example.com", password="moderpass"
        )
        self.moderator.groups.create(name="moderators")
        self.user = CustomUser.objects.create_user(
            email="user@example.com", password="userpass"
        )
        self.other_user = CustomUser.objects.create_user(
            email="other@example.com", password="otherpass"
        )

        # Создаем тестовый курс и уроки
        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание курса", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание урока",
            course=self.course,
            owner=self.user,
            video_link="https://youtube.com/embed/test123",
        )

        # URL для тестирования
        self.lessons_url = reverse("lesson-list")
        self.lesson_detail_url = reverse("lesson-detail", kwargs={"pk": self.lesson.pk})
        self.subscribe_url = reverse("subscribe")
        self.unsubscribe_url = reverse("unsubscribe")

    # ТЕСТЫ ДЛЯ УРОКОВ

    def test_lesson_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.lessons_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_lesson_create_as_owner(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "course": self.course.pk,
            "video_link": "https://youtube.com/embed/new123",
        }
        response = self.client.post(self.lessons_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_update_as_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Обновленный урок"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновленный урок")

    def test_lesson_delete_as_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.lesson_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_lesson_create_validation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "course": self.course.pk,
            "video_link": "https://vimeo.com/test",  # Невалидная ссылка
        }
        response = self.client.post(self.lessons_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_link", response.data)

    # ТЕСТЫ ДЛЯ ПОДПИСОК

    def test_subscribe_as_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscribe_url, {"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_as_authenticated(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.unsubscribe_url, {"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_course_with_subscription_flag(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        url = reverse("course-detail", kwargs={"pk": self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])

    def test_subscribe_duplicate(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.subscribe_url, {"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Subscription.objects.filter(user=self.user, course=self.course).count(), 1
        )

    # ТЕСТЫ НА ДОСТУП

    def test_lesson_update_as_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Попытка изменения"}
        response = self.client.patch(self.lesson_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_subscribe_unauthenticated(self):
        response = self.client.post(self.subscribe_url, {"course_id": self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ТЕСТ ПАГИНАЦИИ

    def test_lesson_pagination(self):
        # Создаем дополнительные уроки
        for i in range(15):
            Lesson.objects.create(
                title=f"Урок {i}", course=self.course, owner=self.user
            )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.lessons_url + "?page=2&page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)

    # ТЕСТ ВАЛИЦАЦИИ ОПИСАНИЯ
    def test_description_with_external_links(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Урок с ссылками",
            "description": "Нельзя https://example.com",
            "course": self.course.pk,
            "video_link": "https://youtube.com/embed/valid",
        }
        response = self.client.post(self.lessons_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
