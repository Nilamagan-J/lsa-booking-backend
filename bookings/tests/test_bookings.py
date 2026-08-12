import pytest
from rest_framework.test import APIClient

from bookings.models import LSAProfile, Parent


@pytest.fixture
def parent():
    return Parent.objects.create(
        name="Test Parent",
        email="parent@test.com",
        phone="+919876543210",
    )


@pytest.fixture
def lsa():
    return LSAProfile.objects.create(
        name="Test LSA",
        email="lsa@test.com",
        specialization="Autism Support",
        hourly_rate=30.00,
        is_available=True,
    )


@pytest.fixture
def client():
    return APIClient()


def booking_payload(parent_id, lsa_id):
    return {
        "parent": parent_id,
        "lsa": lsa_id,
        "booking_date": "2026-08-20",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "notes": "Test booking",
    }


@pytest.mark.django_db
def test_create_booking(client, parent, lsa, monkeypatch):
    def mock_payment(booking):
        return {
            "transaction_id": "txn_test_123",
            "status": "success",
        }

    monkeypatch.setattr(
        "bookings.views.initiate_payment",
        mock_payment,
    )

    response = client.post(
        "/api/v1/bookings/",
        booking_payload(parent.id, lsa.id),
        format="json",
    )

    assert response.status_code == 201
    assert response.data["booking"]["status"] == "confirmed"
    assert response.data["payment"]["status"] == "success"


@pytest.mark.django_db
def test_reject_invalid_time(client, parent, lsa):
    payload = booking_payload(parent.id, lsa.id)
    payload["end_time"] = "09:00:00"

    response = client.post(
        "/api/v1/bookings/",
        payload,
        format="json",
    )

    assert response.status_code == 400
    assert "end_time" in response.data


@pytest.mark.django_db
def test_reject_overlapping_booking(client, parent, lsa, monkeypatch):
    def mock_payment(booking):
        return {
            "transaction_id": "txn_test_123",
            "status": "success",
        }

    monkeypatch.setattr(
        "bookings.views.initiate_payment",
        mock_payment,
    )

    first_response = client.post(
        "/api/v1/bookings/",
        booking_payload(parent.id, lsa.id),
        format="json",
    )

    assert first_response.status_code == 201

    overlapping_payload = booking_payload(parent.id, lsa.id)
    overlapping_payload["start_time"] = "10:30:00"
    overlapping_payload["end_time"] = "11:30:00"

    second_response = client.post(
        "/api/v1/bookings/",
        overlapping_payload,
        format="json",
    )

    assert second_response.status_code == 400

@pytest.mark.django_db
def test_list_available_lsa_resources(client, lsa):
    response = client.get("/api/v1/lsa/resources/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == lsa.id


@pytest.mark.django_db
def test_filter_lsa_resources_by_skill(client, lsa):
    response = client.get(
        "/api/v1/lsa/resources/?skill=Autism"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["specialization"] == "Autism Support"


@pytest.mark.django_db
def test_filter_lsa_resources_returns_empty_for_unknown_skill(
    client,
    lsa,
):
    response = client.get(
        "/api/v1/lsa/resources/?skill=Physics"
    )

    assert response.status_code == 200
    assert response.data == []