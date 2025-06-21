from rest_framework import viewsets
from .models import CustomUser, Payment
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsUser
from .serializers import PaymentSerializer, UserCommonSerializer, CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    model = CustomUser
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if (
            self.action in ("retrieve", "update", "partial_update", "destroy")
            and self.request.user.email == self.get_object().email
        ):
            return CustomUserSerializer
        return UserCommonSerializer

    def get_permissions(self):
        """Права на действия пользователя"""

        if self.action in ("update", "partial_update", "destroy"):
            permission_classes = [IsAuthenticated, IsUser]
        elif self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class PaymentViewSet(viewsets.ModelViewSet):
    model = Payment
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "method"]
    orderind_fields = ["payment_date"]
