from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source="get_notification_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "notification_type", "notification_type_display", "title", "message", "review", "is_read", "read_at", "created_at",)
        read_only_fields = ("id", "notification_type", "notification_type_display", "title", "message", "review", "is_read", "read_at", "created_at",)

class NotificationReadSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ("id", "is_read", "read_at", )
        read_only_fields = ("id", "is_read", "read_at", )

    def validate_is_read(self, value):
        if value is not True:
            raise serializers.ValidationError("A notification can only be marked as read.")
        return value