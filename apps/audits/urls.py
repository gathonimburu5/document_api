from django.urls import path
from .views import (
    AuditLogListAPIView,
    AuditLogDetailAPIView,
    SystemAuditLogListAPIView,
    SystemAuditLogDetailAPIView,
)

urlpatterns = [
    path("", AuditLogListAPIView.as_view(), name="my-logs"),
    path("<int:pk>/", AuditLogDetailAPIView.as_view(), name="my-log-details"),
    path("system/", SystemAuditLogListAPIView.as_view(), name="system-log"),
    path("system/<int:pk>/", SystemAuditLogDetailAPIView.as_view(), name="system-log-details"),
]
