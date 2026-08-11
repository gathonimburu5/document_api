from rest_framework import serializers
from .models import AuditLog

class AuditLogListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    class Meta:
        model = AuditLog
        fields = ("id", "user", "user_email", "user_name", "action", "action_display", "description", "method", "endpoint", "ip_address", "status", "metadata", "created_at")
        read_only_fields = fields

    def get_user_name(self, obj):
        if not obj.user:
            return None
        return obj.user.get_full_name() or obj.user.email

class AuditLogDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    class Meta:
        model = AuditLog
        fields = ("id", "user", "user_email", "user_name", "action", "action_display", "description", "method", "endpoint", "ip_address", "status", "metadata", "created_at")
        read_only_fields = fields

    def get_user_name(self, obj):
        if not obj.user:
            return None
        return obj.user.get_full_name() or obj.user.email