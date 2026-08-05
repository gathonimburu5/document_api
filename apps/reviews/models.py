from django.db import models
from django.conf import settings
from apps.documents.models import Document, DocumentVersion
import uuid

class StatusChoices(models.TextChoices):
    DRAFT = "DRAFT", "draft"
    SUBMITTED = "SUBMITTED", "submitted"
    IN_REVIEW = "IN REVIEW", "in_review"
    CHANGES_REQUESTED = "CHANGES REQUESTED", "changes_requested"
    APPROVED = "APPROVED", "approved"
    REJECTED = "REJECTED", "rejected"

class DecisionChoices(models.TextChoices):
    APPROVE = 'aprove', 'Aprove'
    REJECT = 'reject', 'Reject'
    REQUEST_CHANGES = 'request_changes', 'Request Changes'

class ReviewRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="reviews")
    version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_reviews")
    status = models.CharField(max_length=30, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=False)

class ReviewAssignment(models.Model):
    review = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE, related_name="assignments")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("review", "reviewer")

class Comment(models.Model):
    review = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

class ReviewDecision(models.Model):
    review = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE, related_name='decisions')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    decision = models.CharField(max_length=20, choices=DecisionChoices.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
