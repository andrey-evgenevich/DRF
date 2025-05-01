from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'preview', 'video_link', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons.all')

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'created_at', 'updated_at',  'lessons_count', 'lessons']


    def get_lessons_count(self, obj):
        return obj.lessons.count()

