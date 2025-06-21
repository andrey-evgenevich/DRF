from rest_framework.serializers import ValidationError


def validate_url(value):
    if "youtube.com" not in value:
        raise ValidationError("Введенная ссылка запрещена.")
