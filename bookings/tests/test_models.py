import pytest

from bookings.models import Booking, LSAProfile, Parent


@pytest.mark.django_db
def test_booking_belongs_to_parent_and_lsa():
    parent = Parent.objects.create(
        name="Test Parent",
        email="parent@test.com",
        phone="+919876543210",
    )

    lsa = LSAProfile.objects.create(
        name="Test LSA",
        email="lsa@test.com",
        specialization="Autism Support",
        hourly_rate=30.00,
        is_available=True,
    )

    booking = Booking.objects.create(
        parent=parent,
        lsa=lsa,
        booking_date="2026-08-20",
        start_time="10:00:00",
        end_time="11:00:00",
        notes="Model relationship test",
    )

    assert booking.parent == parent
    assert booking.lsa == lsa