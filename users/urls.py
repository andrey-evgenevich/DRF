from rest_framework.routers import SimpleRouter
from django.urls import path

from .views import CustomUserViewSet, PaymentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "users"

router_user = SimpleRouter()
router_payment = SimpleRouter()

router_user.register("user", CustomUserViewSet)
router_payment.register("payment", PaymentViewSet)

urlpatterns = (
    router_user.urls
    + router_payment.urls
    + [
        path("login/", TokenObtainPairView.as_view(), name="login"),
        path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    ]
)
