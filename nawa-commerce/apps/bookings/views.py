from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, serializers, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, ServiceSlot
from .services import book_slot


class ServiceSlotSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServiceSlot
        fields = ["id", "product", "start_at", "duration_minutes", "capacity", "is_available"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "slot", "status", "created_at"]
        read_only_fields = ["status", "created_at"]


class ServiceSlotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceSlotSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["product"]

    def get_queryset(self):
        return ServiceSlot.objects.filter(start_at__gte=timezone.now())


@extend_schema(exclude=True)


class BookSlotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slot_id):
        slot = get_object_or_404(ServiceSlot, pk=slot_id)
        booking = book_slot(slot, request.user)
        return Response(BookingSerializer(booking).data, status=201)
