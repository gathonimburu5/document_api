from django.db import models
import uuid
from django.conf import settings
from apps.reviews.models import ReviewRequest

class NotificationTypeChoices(models.TextChoices):
    REVIEW_SUBMITTED = "REVIEW_SUBMITTED", "Review Submitted"
    REVIEW_ASSIGNED = "REVIEW_ASSIGNED", "Review Assigned"
    REVIEW_STARTED = "REVIEW_STARTED", "Review Started"
    DECISION_SUBMITTED = "DECISION_SUBMITTED", "Decision Submitted"
    REVIEW_APPROVED = "REVIEW_APPROVED", "Review Approved"
    REVIEW_REJECTED = "REVIEW_REJECTED", "Review Rejected"
    CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"
    COMMENT_ADDED = "COMMENT_ADDED", "Comment Added"
class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=50, choices=NotificationTypeChoices.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    review = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.title}"