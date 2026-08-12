from django.urls import path

from .views import BookingCreateView, LSAResourceListView


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
]