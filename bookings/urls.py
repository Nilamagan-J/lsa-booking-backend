from django.urls import path

from .views import (
    BookingCreateView,
    LSAResourceListView,
    MockPaymentView,
    PaymentWebhookView,
)


urlpatterns = [
    path(
        "bookings/",
        BookingCreateView.as_view(),
        name="booking-create",
    ),
    path(
        "lsa/resources/",
        LSAResourceListView.as_view(),
        name="lsa-resources",
    ),
    path(
        "mock-payment/",
        MockPaymentView.as_view(),
        name="mock-payment",
    ),
    path(
        "payments/webhook/",
        PaymentWebhookView.as_view(),
        name="payment-webhook",
    ),
]