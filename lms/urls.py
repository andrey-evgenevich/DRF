from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView, SubscriptionViewSet, \
    PaymentCreateAPIView, PaymentStatusAPIView, PaymentSuccessView, PaymentCancelView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
    path('subscribe/', SubscriptionViewSet.as_view({'post': 'subscribe'}), name='subscribe'),
    path('unsubscribe/', SubscriptionViewSet.as_view({'post': 'unsubscribe'}), name='unsubscribe'),
    path('payments/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentStatusAPIView.as_view(), name='payment-status'),
    path('payments/<int:pk>/success/', PaymentSuccessView, name='payment-success'),
    path('payments/<int:pk>/cancel/', PaymentCancelView, name='payment-cancel'),
]
