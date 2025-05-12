from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from rest_framework import viewsets, status
from .models import Course, Lesson, Payment
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from config.users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from .models import Subscription
from .serializers import SubscriptionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .paginators import CoursePaginator, LessonPaginator
from django.urls import reverse

from .services.stripe_service import create_stripe_product, create_stripe_price, create_stripe_session, \
    get_stripe_session


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdminUser | IsOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action in ['retrieve', 'list']:
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
                        user=self.request.user,
                        course=OuterRef('pk')
                    )
                )
            )
        return queryset


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdminUser | IsOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user.is_staff or self.request.user.groups.filter(name='moderators').exists()):
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

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            course_id=course_id
        )

        if created:
            return Response({'status': 'подписка создана'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'вы уже подписаны'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = Subscription.objects.filter(
            user=request.user,
            course_id=course_id
        ).delete()

        if deleted:
            return Response({'status': 'подписка удалена'}, status=status.HTTP_200_OK)
        return Response({'status': 'подписка не найдена'}, status=status.HTTP_404_NOT_FOUND)


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