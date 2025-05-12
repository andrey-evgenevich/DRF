from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Course, Lesson, Subscription, Payment
from .validators import validate_no_external_links

class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'preview', 'video_link', 'created_at', 'updated_at']
        extra_kwargs = {
            'video_link': {
                'validators': [validate_no_external_links]
            }
        }


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons.all')
    is_subscribed = serializers.SerializerMethodField()
    owner = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'created_at', 'updated_at',  'lessons_count', 'lessons']


    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'course', 'subscribed_at']
        read_only_fields = ['subscribed_at']

class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
