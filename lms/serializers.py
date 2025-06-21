from .models import Course, Lesson, CourseSubscription, CoursePayment
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from lms.validators import validate_url


class LessonSerializer(ModelSerializer):
    url = serializers.URLField(validators=[validate_url])

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSubscriptionSerializer(ModelSerializer):

    class Meta:
        model = CourseSubscription
        fields = ["course"]


class CourseSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True)
    subscription = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_subscription(self, course):
        currency_user = self.context.get("request", None).user
        return course.course_subscription.filter(user=currency_user).exists()

    def get_lessons_count(self, course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = "__all__"


class CoursePaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoursePayment
        fields = "__all__"
