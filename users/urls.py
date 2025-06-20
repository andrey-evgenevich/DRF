from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    PaymentCreateAPIView,
    PaymentStatusAPIView,
    PaymentSuccessView,
    PaymentCancelView,
)
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserListView, UserDetailView, RegisterView, CustomTokenObtainPairView

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("me/", UserDetailView.as_view(), name="current-user"),
    path("payments/", PaymentCreateAPIView.as_view(), name="payment-create"),
    path("payments/<int:pk>/", PaymentStatusAPIView.as_view(), name="payment-status"),
    path("payments/<int:pk>/success/", PaymentSuccessView, name="payment-success"),
    path("payments/<int:pk>/cancel/", PaymentCancelView, name="payment-cancel"),
]
