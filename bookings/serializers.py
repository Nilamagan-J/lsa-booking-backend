from django.utils import timezone
from rest_framework import serializers

from .models import Booking, LSAProfile, Parent


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "parent",
            "lsa",
            "booking_date",
            "start_time",
            "end_time",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        booking_date = attrs.get("booking_date")
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        lsa = attrs.get("lsa")

        if booking_date < timezone.localdate():
            raise serializers.ValidationError(
                {"booking_date": "Booking date cannot be in the past."}
            )

        if end_time <= start_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        conflicting_booking = Booking.objects.filter(
            lsa=lsa,
            booking_date=booking_date,
            status__in=[
                Booking.Status.PENDING,
                Booking.Status.CONFIRMED,
            ],
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        if conflicting_booking:
            raise serializers.ValidationError(
                "The LSA already has a booking that overlaps this time."
            )

        return attrs

class LSAProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LSAProfile
        fields = [
            "id",
            "name",
            "email",
            "specialization",
            "hourly_rate",
            "is_available",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]