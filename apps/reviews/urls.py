from django.urls import path
from .views import (
    ReviewRequestListAPIView,
    ReviewRequestCreateAPIView,
    ReviewRequestDetailAPIView,
    ReviewRequestSubmitAPIView,
    ReviewAssignmentAPIView,
    ReviewStartAPIView,
    ReviewDecisionCreateAPIView,
    ReviewCommentAPIView
)

urlpatterns = [
    path("", ReviewRequestListAPIView.as_view(), name="review-list"),
    path("create/", ReviewRequestCreateAPIView.as_view(), name="review-create"),
    path("<uuid:pk>/", ReviewRequestDetailAPIView.as_view(), name="review-details"),
    path("<uuid:pk>/submit/", ReviewRequestSubmitAPIView.as_view(), name="review-submit"),
    path("<uuid:pk>/assign/", ReviewAssignmentAPIView.as_view(), name="review-assignment"),
    path("<uuid:pk>/start/", ReviewStartAPIView.as_view(), name="review-start"),
    path("assignment/<int:assignment_id>/decision/", ReviewDecisionCreateAPIView.as_view(), name="assignment-decision"),
    path("<uuid:pk>/comment/", ReviewCommentAPIView.as_view(), name="review-comment"),
]
