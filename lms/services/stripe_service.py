import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course):
    """Создание продукта в Stripe"""
    product = stripe.Product.create(
        name=course.title,
        description=course.description[:500] if course.description else None,
        metadata={
            "course_id": course.id,
        },
    )
    return product


def create_stripe_price(product_id, amount):
    """Создание цены в Stripe"""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),  # Конвертация в копейки
        currency="rub",
    )
    return price


def create_stripe_session(price_id, success_url, cancel_url):
    """Создание сессии оплаты в Stripe"""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session


def get_stripe_session(session_id):
    """Получение информации о сессии оплаты"""
    return stripe.checkout.Session.retrieve(session_id)
