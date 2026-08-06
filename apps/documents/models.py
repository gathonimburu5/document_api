from django.db import models
from django.conf import settings
from apps.commons.utils import validate_file_size
import uuid

class DocumentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

    def owned_by(self, user):
        return self.filter(owner=user)

    def drafts(self):
        return self.filter(status=DocumentStatus.DRAFT)

    def submitted(self):
        return self.filter(status=DocumentStatus.SUBMITTED)

    def under_review(self):
        return self.filter(status=DocumentStatus.UNDER_REVIEW)

    def approved(self):
        return self.filter(status=DocumentStatus.APPROVED)

    def rejected(self):
        return self.filter(status=DocumentStatus.REJECTED)

    def with_details(self):
        return self.select_related("owner").prefetch_related("versions", "versions__uploaded_by")

    def with_related(self):
        return self.select_related("owner").prefetch_related("versions")

class DocumentStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    reject_reason = models.TextField(blank=True)
    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="rejected_documents")
    rejected_at = models.DateTimeField(null=True, blank=True)
    objects = DocumentQuerySet.as_manager()

    def __str__(self):
        return self.title

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to="documents/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-version_number']
        constraints = [models.UniqueConstraint(fields=['document', 'version_number'], name="unique_document_version")]