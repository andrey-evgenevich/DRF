from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


def validate_no_external_links(text):
    """Проверяет текст на отсутствие сторонних ссылок"""
    if text:
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain.endswith('youtube.com') or domain.endswith('youtu.be'):
                raise ValidationError(
                    'В описании запрещены ссылки на сторонние ресурсы кроме YouTube'
                )