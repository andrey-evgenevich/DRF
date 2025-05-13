from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from rest_framework import viewsets, generics, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
from config.lms.models import Course
from config.lms.services.stripe_service import get_stripe_session, create_stripe_product, create_stripe_price, \
    create_stripe_session


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        return self.request.user

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Создаем запись о платеже
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            status='pending'
        )

        # Создаем продукт и цену в Stripe
        try:
            product = create_stripe_product(course)
            price = create_stripe_price(product.id, float(course.price))

            # Создаем сессию оплаты
            success_url = request.build_absolute_uri(
                reverse('payment-success', kwargs={'pk': payment.pk})
            )
            cancel_url = request.build_absolute_uri(
                reverse('payment-cancel', kwargs={'pk': payment.pk})
            )

            session = create_stripe_session(
                price.id,
                success_url,
                cancel_url
            )

            # Обновляем платеж
            payment.stripe_product_id = product.id
            payment.stripe_price_id = price.id
            payment.stripe_session_id = session.id
            payment.payment_url = session.url
            payment.save()

            return Response({
                'payment_id': payment.id,
                'payment_url': session.url,
                'status': 'pending'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentStatusAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    def get(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.user != request.user:
            return Response(
                {'error': 'Доступ запрещен'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем статус в Stripe
        try:
            session = get_stripe_session(payment.stripe_session_id)
            if session.payment_status == 'paid':
                payment.status = 'paid'
                payment.save()

            return Response({
                'payment_id': payment.id,
                'status': payment.status,
                'stripe_status': session.payment_status
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentSuccessView(View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        # Можно добавить логику при успешной оплате
        return redirect(f'https://your-frontend.com/payment/success/{pk}/')

class PaymentCancelView(View):
    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        # Можно добавить логику при отмене оплаты
        return redirect(f'https://your-frontend.com/payment/cancel/{pk}/')