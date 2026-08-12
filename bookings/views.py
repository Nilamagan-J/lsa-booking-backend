from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BookingSerializer


class BookingCreateView(APIView):
    def post(self, request):
        serializer = BookingSerializer(data=request.data)

        if serializer.is_valid():
            booking = serializer.save()

            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )