from django.db import models
from django.conf import settings
from apps.documents.models import Document, DocumentVersion
import uuid

class ReviewStatusChoices(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    IN_REVIEW = "IN_REVIEW", "In Review"
    CHANGES_REQUESTED = "CHANGES_REQUESTED", "Changes Requested"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

class ReviewDecisionChoices(models.TextChoices):
    APPROVE = 'APPROVE', 'Approve'
    REJECT = 'REJECT', 'Reject'
    REQUEST_CHANGES = 'REQUEST_CHANGES', 'Request Changes'

class ReviewAssignmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_REVIEW = "IN_REVIEW", "In Review"
    COMPLETED = "COMPLETED", "Completed"
    SKIPPED = "SKIPPED", "Skipped"

class ReviewQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=ReviewStatusChoices.DRAFT)
    def pending(self):
        return self.filter(status=ReviewStatusChoices.SUBMITTED)
    def in_review(self):
        return self.filter(status=ReviewStatusChoices.IN_REVIEW)
    def approved(self):
        return self.filter(status=ReviewStatusChoices.APPROVED)
    def rejected(self):
        return self.filter(status=ReviewStatusChoices.REJECTED)
    def requested_by(self, user):
        return self.filter(requester=user)
    def for_document(self, document):
        return self.filter(document=document)
    def for_version(self, version):
        return self.filter(version=version)
    def assigned_to(self, user):
        return self.filter(assignments__reviewer=user).distinct()
    def with_details(self):
        return (self.select_related("document", "version", "requester").prefetch_related("assignments", "assignments__reviewer", "assignments__decision", "comments", "comments__author"))

class ReviewRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="reviews")
    version = models.ForeignKey(DocumentVersion, on_delete=models.CASCADE, related_name="review_requests")
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_reviews")
    status = models.CharField(max_length=30, choices=ReviewStatusChoices.choices, default=ReviewStatusChoices.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    objects = ReviewQuerySet.as_manager()

class ReviewAssignment(models.Model):
    review = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE, related_name="assignments")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ReviewAssignmentStatus.choices, default=ReviewAssignmentStatus.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["review", "reviewer"], name="unique_review_assignment")]

class Comment(models.Model):
    review = models.ForeignKey(ReviewRequest, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

class ReviewDecision(models.Model):
    assignment  = models.OneToOneField(ReviewAssignment, on_delete=models.CASCADE, related_name='decision')
    decision = models.CharField(max_length=20, choices=ReviewDecisionChoices.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
