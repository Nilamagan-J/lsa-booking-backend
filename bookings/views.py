import uuid

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, LSAProfile, Payment
from .serializers import BookingSerializer, LSAProfileSerializer
from .services import PaymentServiceError, initiate_payment
from django.shortcuts import render

class BookingCreateView(APIView):
    def post(self, request):
        serializer = BookingSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = serializer.save()

        try:
            payment_result = initiate_payment(booking)

        except PaymentServiceError as exc:
            booking.delete()

            return Response(
                {
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        Payment.objects.create(
            booking=booking,
            amount=booking.lsa.hourly_rate,
            status=payment_result["status"],
            transaction_id=payment_result["transaction_id"],
        )

        if payment_result["status"] == "success":
            booking.status = Booking.Status.CONFIRMED
            booking.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "booking": BookingSerializer(booking).data,
                "payment": payment_result,
            },
            status=status.HTTP_201_CREATED,
        )


class LSAResourceListView(APIView):
    def get(self, request):
        queryset = LSAProfile.objects.filter(
            is_available=True
        ).order_by("name")

        skill = request.query_params.get("skill")

        if skill:
            queryset = queryset.filter(
                specialization__icontains=skill
            )

        serializer = LSAProfileSerializer(queryset, many=True)

        return Response(serializer.data)


class MockPaymentView(APIView):
    def post(self, request):
        booking_id = request.data.get("booking_id")
        amount = request.data.get("amount")
        currency = request.data.get("currency")

        if not booking_id or not amount or not currency:
            return Response(
                {
                    "status": "failed",
                    "message": "Missing required payment fields.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status": "success",
                "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
                "booking_id": booking_id,
                "amount": amount,
                "currency": currency,
            },
            status=status.HTTP_200_OK,
        )

class PaymentWebhookView(APIView):
    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        payment_status = request.data.get("status")

        if not transaction_id or not payment_status:
            return Response(
                {
                    "error": "transaction_id and status are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payment_status not in {"success", "failed"}:
            return Response(
                {
                    "error": "Invalid payment status."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment = Payment.objects.select_related("booking").get(
                transaction_id=transaction_id
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "error": "Payment not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        payment.status = payment_status
        payment.save(update_fields=["status", "updated_at"])

        booking = payment.booking

        if payment_status == "success":
            booking.status = Booking.Status.CONFIRMED
        else:
            booking.status = Booking.Status.CANCELLED

        booking.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "message": "Payment status updated successfully.",
                "payment": {
                    "transaction_id": payment.transaction_id,
                    "status": payment.status,
                },
                "booking": {
                    "id": booking.id,
                    "status": booking.status,
                },
            },
            status=status.HTTP_200_OK,
        )

def home(request):
    return render(request, "bookings/home.html")