from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BookingSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LSAProfile
from .serializers import BookingSerializer, LSAProfileSerializer

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