from .models import CustomUser, Payment
from rest_framework.serializers import ModelSerializer


class PaymentSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


class CustomUserSerializer(ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", 'phone', 'city']
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Удаляем пароль из данных, чтобы использовать set_password
        password = validated_data.pop("password", None)
        user = CustomUser(**validated_data)  # Передаем остальные поля
        if password:
            user.set_password(password)  # Хешируем пароль
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)  # Хешируем пароль
            instance.save()  # Сохраняем изменения после установки пароля
        return super().update(instance, validated_data)


class UserCommonSerializer(ModelSerializer):
    """Сериализатор для пользователя"""

    class Meta:
        model = CustomUser
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Хешируем пароль с использованием set_password
        password = validated_data.pop("password", None)
        user = CustomUser(email=validated_data["email"])
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Хешируем пароль при обновлении, если пароль предоставлен
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)  # Хешируем пароль
            instance.save()  # Сохраняем изменения после установки пароля
        return super().update(instance, validated_data)
