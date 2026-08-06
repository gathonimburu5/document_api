from apps.documents.models import Document, DocumentVersion, DocumentStatus
from django.db import transaction
from apps.audits.models import AuditAction
from .audit_services import AuditService
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import os

class DocumentService:
    INITIAL_VERSION = 1

    @staticmethod
    def _create_version(*, document, version_no, uploaded_by, validated_data):
        return DocumentVersion.objects.create(document=document, version_number=version_no, file=validated_data["file"], uploaded_by=uploaded_by, notes=validated_data.get("notes", ""))

    @staticmethod
    def _next_version(*, document):
        latest = (document.versions.first())
        next = DocumentService.INITIAL_VERSION if latest is None else latest.version_number + DocumentService.INITIAL_VERSION
        return next

    @staticmethod
    @transaction.atomic
    def create_document(*, owner, request, validated_data) -> Document:
        document = Document.objects.create(owner=owner, title=validated_data["title"], description=validated_data.get("description", ""))
        # create the document versions
        DocumentService._create_version(document=document, version_no=DocumentService.INITIAL_VERSION, uploaded_by=owner, validated_data=validated_data)
        AuditService.log(
            user=owner,
            request=request,
            action=AuditAction.CREATE,
            description=f"Document {document.title} created successfully.",
            metadata={
                "document_id": str(document.id),
                "document_title":document.title,
                "version": DocumentService.INITIAL_VERSION,
            },
        )
        return document

    @staticmethod
    @transaction.atomic
    def upload_new_version(*, document, request, owner, validated_data):
        document = (Document.objects.select_for_update().get(pk=document.pk))
        # latest_version = (document.versions.first())
        # .filter(document=document).order_by("-version_number").first()
        new_version = DocumentService._next_version(document=document)
        if document.status != DocumentStatus.SUBMITTED:
            raise ValidationError("Only submitted documents cannot receive new versions.")

        if document.is_archived:
            raise ValidationError("Archived documents cannot be modified.")

        version = DocumentService._create_version(document=document, version_no=new_version, uploaded_by=owner, validated_data=validated_data)
        AuditService.log(
            user=owner,
            request=request,
            action=AuditAction.UPDATE,
            description=f"uploaded version {new_version} for {document.title}.",
            metadata={
                "document_id":str(document.id),
                "document_title":document.title,
                "document_version": new_version,
            },
        )
        return version

    @staticmethod
    @transaction.atomic
    def archive_document(*, document, user, request):
        document = (Document.objects.select_for_update().get(pk=document.pk))
        if document.is_archived:
            raise ValidationError("Document is already archived.")

        document.is_archived = True
        document.save(update_fields=["is_archived", "updated_at"])

        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.IS_ARCHIVED,
            description=f"document ({document.title}) successfully archived.",
            metadata={
                "document_id":str(document.id),
                "document_title":document.title,
            }
        )

    @staticmethod
    @transaction.atomic
    def update_document(*, document, user, request, validated_data) -> Document:
        document = (Document.objects.select_for_update().get(pk=document.pk))
        if document.is_archived:
            raise ValidationError("Archived document cannot be updated.")
        if document.status != DocumentStatus.SUBMITTED:
            raise ValidationError("Only submitted document can be edited.")

        document.title = validated_data.get("title", document.title)
        document.description = validated_data.get("description", document.description)
        document.save(update_fields=["title", "description", "updated_at"])

        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.UPDATE,
            description=f"document ({document.title}) updated successfully.",
            metadata={
                "document_id":str(document.id),
                "document_title":document.title,
            }
        )

    @staticmethod
    def get_latest_version(*, document):
        latest_version = (document.versions.first())
        return latest_version

    @staticmethod
    @transaction.atomic
    def submit_document(*, document, user, request):
        document = (Document.objects.select_for_update().get(pk=document.pk))
        if document.status != DocumentStatus.DRAFT:
            raise ValidationError("Only document in draft state can be submitted.")

        document.status = DocumentStatus.SUBMITTED
        document.save(update_fields=["status", "updated_at"])

        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.SUBMITTED,
            description=f"document ({document.title}) successfully submitted.",
            metadata={
                "document_id":str(document.id),
                "document_title":document.title,
                "document_status":document.status,
            }
        )

    @staticmethod
    @transaction.atomic
    def reject_document(*, document, user, request, validated_data):
        document = (Document.objects.select_for_update().get(pk=document.pk))
        if document.status != DocumentStatus.UNDER_REVIEW:
            raise ValidationError("Only document under review can be rejected")

        document.status = DocumentStatus.REJECTED
        document.reject_reason = validated_data.get("reject_reason", document.reject_reason)
        document.rejected_at = timezone.now()
        document.save(update_fields=["status", "reject_reason", "rejected_at", "updated_at"])

        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.REJECTED,
            description=f"document ({document.title}) rejected successfully.",
            metadata={
                "document_id": str(document.id),
                "document_title": document.title,
                "document_status": document.status,
            }
        )

    @staticmethod
    @transaction.atomic
    def approve_document(*, document, user, request):
        document = (Document.objects.select_for_update().get(pk=document.pk))
        if document.status != DocumentStatus.UNDER_REVIEW:
            raise ValidationError("Only document under review can be approved")

        document.status = DocumentStatus.APPROVED
        document.save(update_fields=["status", "updated_at"])

        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.APPROVED,
            description=f"document ({document.title}) approved successfully.",
            metadata={
                "document_id":str(document.id),
                "document_title":document.title,
                "document_status":document.status,
            }
        )

    @staticmethod
    @transaction.atomic
    def restore_document(*, document, user, request):
        document = (Document.objects.select_for_update().get(pk=document.pk))
        if not document.is_archived:
            raise ValidationError("Only archieved document can be restored.")

        document.is_archived = False
        document.save(update_fields=["is_archived", "updated_at"])

        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.RESTORED,
            description=f"document ({document.title}) successfully restored.",
            metadata={
                "document_id":str(document.id),
                "document_title":document.title,
            }
        )


