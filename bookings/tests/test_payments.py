import pytest
from rest_framework.test import APIClient

from bookings.models import Booking, LSAProfile, Parent


@pytest.fixture
def payment_data():
    parent = Parent.objects.create(
        name="Payment Test Parent",
        email="payment-parent@test.com",
        phone="+919876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Payment Test LSA",
        email="payment-lsa@test.com",
        specialization="Autism Support",
        hourly_rate=30.00,
        is_available=True,
    )

    return parent, lsa


@pytest.fixture
def payment_client():
    return APIClient()


def create_booking(payment_client, parent, lsa, monkeypatch):
    def mock_payment(booking):
        return {
            "transaction_id": "txn_payment_test",
            "status": "success",
        }

    monkeypatch.setattr(
        "bookings.views.initiate_payment",
        mock_payment,
    )

    response = payment_client.post(
        "/api/v1/bookings/",
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "booking_date": "2026-08-25",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "notes": "Payment test booking",
        },
        format="json",
    )

    return response


@pytest.mark.django_db
def test_successful_payment_creates_confirmed_booking(
    payment_client,
    payment_data,
    monkeypatch,
):
    parent, lsa = payment_data

    response = create_booking(
        payment_client,
        parent,
        lsa,
        monkeypatch,
    )

    assert response.status_code == 201
    assert response.data["payment"]["status"] == "success"
    assert response.data["booking"]["status"] == "confirmed"


@pytest.mark.django_db
def test_payment_failure_returns_bad_gateway(
    payment_client,
    payment_data,
    monkeypatch,
):
    parent, lsa = payment_data

    def failed_payment(booking):
        from bookings.services import PaymentServiceError

        raise PaymentServiceError(
            "Payment service timed out."
        )

    monkeypatch.setattr(
        "bookings.views.initiate_payment",
        failed_payment,
    )

    response = payment_client.post(
        "/api/v1/bookings/",
        {
            "parent": parent.id,
            "lsa": lsa.id,
            "booking_date": "2026-08-26",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "notes": "Payment failure test",
        },
        format="json",
    )

    assert response.status_code == 502
    assert response.data["error"] == "Payment service timed out."


@pytest.mark.django_db
def test_payment_webhook_success(
    payment_client,
    payment_data,
    monkeypatch,
):
    parent, lsa = payment_data

    response = create_booking(
        payment_client,
        parent,
        lsa,
        monkeypatch,
    )

    transaction_id = response.data["payment"]["transaction_id"]

    webhook_response = payment_client.post(
        "/api/v1/payments/webhook/",
        {
            "transaction_id": transaction_id,
            "status": "success",
        },
        format="json",
    )

    assert webhook_response.status_code == 200
    assert webhook_response.data["payment"]["status"] == "success"
    assert webhook_response.data["booking"]["status"] == "confirmed"


@pytest.mark.django_db
def test_payment_webhook_rejects_invalid_status(
    payment_client,
    payment_data,
    monkeypatch,
):
    parent, lsa = payment_data

    response = create_booking(
        payment_client,
        parent,
        lsa,
        monkeypatch,
    )

    transaction_id = response.data["payment"]["transaction_id"]

    webhook_response = payment_client.post(
        "/api/v1/payments/webhook/",
        {
            "transaction_id": transaction_id,
            "status": "banana",
        },
        format="json",
    )

    assert webhook_response.status_code == 400
    assert webhook_response.data["error"] == "Invalid payment status."


@pytest.mark.django_db
def test_payment_webhook_rejects_unknown_transaction(
    payment_client,
):
    response = payment_client.post(
        "/api/v1/payments/webhook/",
        {
            "transaction_id": "txn_does_not_exist",
            "status": "success",
        },
        format="json",
    )

    assert response.status_code == 404
    assert response.data["error"] == "Payment not found."