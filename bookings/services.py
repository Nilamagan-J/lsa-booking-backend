import logging
import os

import requests

from .models import Booking


logger = logging.getLogger(__name__)


class PaymentServiceError(Exception):
    """Raised when the payment service cannot process a request."""


def initiate_payment(booking: Booking) -> dict:
    payment_url = os.getenv("PAYMENT_API_URL")
    timeout = int(os.getenv("PAYMENT_API_TIMEOUT", "5"))

    if not payment_url:
        logger.error(
            "Payment API URL is not configured for booking %s",
            booking.id,
        )
        raise PaymentServiceError(
            "Payment API URL is not configured."
        )

    payload = {
        "booking_id": booking.id,
        "amount": str(booking.lsa.hourly_rate),
        "currency": "USD",
    }

    logger.info(
        "Initiating payment for booking %s",
        booking.id,
    )

    try:
        response = requests.post(
            payment_url,
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()

    except requests.Timeout as exc:
        logger.error(
            "Payment request timed out for booking %s",
            booking.id,
        )
        raise PaymentServiceError(
            "Payment service timed out."
        ) from exc

    except requests.RequestException as exc:
        logger.error(
            "Payment request failed for booking %s: %s",
            booking.id,
            exc,
        )
        raise PaymentServiceError(
            "Payment service request failed."
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error(
            "Payment service returned invalid JSON for booking %s",
            booking.id,
        )
        raise PaymentServiceError(
            "Payment service returned an invalid response."
        ) from exc

    transaction_id = data.get("transaction_id")
    payment_status = data.get("status")

    if not transaction_id or payment_status not in {
        "success",
        "pending",
        "failed",
    }:
        logger.error(
            "Unexpected payment response for booking %s: %s",
            booking.id,
            data,
        )
        raise PaymentServiceError(
            "Payment service returned an unexpected response."
        )

    logger.info(
        "Payment initiated for booking %s with transaction %s",
        booking.id,
        transaction_id,
    )

    return {
        "transaction_id": transaction_id,
        "status": payment_status,
    }