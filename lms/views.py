from django.shortcuts import render
from rest_framework import viewsets
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework import generics
from django.db.models import Prefetch

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.all())
    ).all()
    serializer_class = CourseSerializer

class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer