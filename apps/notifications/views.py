from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.commons.responses import CustomResponse
from django.shortcuts import get_object_or_404
from .serializers import NotificationSerializer, NotificationReadSerializer
from .models import Notification
from django.utils import timezone

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=NotificationSerializer(many=True), description="Notification list")
    def get(self, request):
        notifications = (Notification.objects.filter(recipient=request.user).select_related("review", "review__document").order_by("-created_at"))
        serializer = NotificationSerializer(notifications, many=True)
        return CustomResponse.success(message="Retrieved notification successful.", data=serializer.data)

class NotificationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: NotificationSerializer},
        description="Notification details"
    )
    def get(self, request, pk):
        notification = get_object_or_404(Notification.objects.select_related("review", "review__document"), id=pk, recipient=request.user)
        serializer = NotificationSerializer(notification)
        return CustomResponse.success(message="Notification retrieved successful.", data=serializer.data,)

class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=NotificationReadSerializer,
        responses={200: NotificationSerializer, 404: "Bad Request"},
        description="Notification marked as read"
    )
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        serializer = NotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
        response_serializer = NotificationSerializer(notification)
        return CustomResponse.success(message="Notification marked as read.", data=response_serializer.data, status=status.HTTP_200_OK)

class NotificationReadAllAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: NotificationSerializer(many=True), 404: "Bad Request"},
        description="Update all notifications"
    )
    def patch(self, request):
        now = timezone.now()
        notifications = Notification.objects.filter(recipient=request.user, is_read=False,)
        notifications.update(is_read=True, read_at=now)
        return CustomResponse.success(message="All Notifications marked as read.", data={"updated_count":notifications.count(),}, status=status.HTTP_200_OK)
