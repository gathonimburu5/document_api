from django.urls import path
from .views import (
    NotificationListAPIView,
    NotificationDetailAPIView,
    NotificationReadAPIView,
    NotificationReadAllAPIView
)

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("<uuid:pk>/", NotificationDetailAPIView.as_view(), name="notification-details"),
    path("<uuid:pk>/read/", NotificationReadAPIView.as_view(), name="notification-read"),
    path("read-all/", NotificationListAPIView.as_view(), name="notification-read-all"),
]
