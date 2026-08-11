from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema
from apps.commons.responses import CustomResponse
from django.shortcuts import get_object_or_404
from .models import AuditLog
from .serializers import AuditLogListSerializer, AuditLogDetailSerializer


class AuditLogListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: AuditLogListSerializer(many=True)},
        description="Audit logs list",
    )
    def get(self, request):
        logs = (AuditLog.objects.filter(user=request.user).select_related("user").order_by("-created_at"))
        serializer = AuditLogListSerializer(logs, many=True)
        return CustomResponse.success(message="Audit logs retrieved successfully.", data=serializer.data)

class AuditLogDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request= None,
        responses={200: AuditLogDetailSerializer},
        description="Audit log details",
    )
    def get(self, request, pk):
        log = get_object_or_404(AuditLog.objects.select_related("user"), id=pk, user=request.user)
        serializer = AuditLogDetailSerializer(log)
        return CustomResponse.success(message="Audit logs detail retrieved successfully.", data=serializer.data)

class SystemAuditLogListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        request=None,
        responses={200: AuditLogListSerializer(many=True)},
        description="System audit log list",
    )
    def get(self, request):
        logs = (AuditLog.objects.select_related("user").order_by("-created_at"))
        serializer = AuditLogListSerializer(logs, many=True)
        return CustomResponse.success(message="System audit logs retrieved successfully.", data=serializer.data)

class SystemAuditLogDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, pk):
        log = get_object_or_404(AuditLog.objects.select_related("user"), id=pk)
        serializer = AuditLogDetailSerializer(log)
        return CustomResponse.success(message="System audit log retrieved successfully.", data=serializer.data)