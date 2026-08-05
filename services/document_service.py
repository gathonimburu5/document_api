from apps.documents.models import Document, DocumentVersion
from django.db import transaction
from apps.audits.models import AuditAction
from .audit_services import AuditService
import os

class DocumentService:
    @staticmethod
    @transaction.atomic
    def create_document(*, owner, request, validated_data):
        document = Document.objects.create(owner=owner, title=validated_data["title"], description=validated_data.get("description", ""))
        # create the document versions
        DocumentVersion.objects.create(document=document, version_number=1, file=validated_data["file"], uploaded_by=owner, notes=validated_data.get("notes", ""))
        AuditService.log(
            user=owner,
            request=request,
            action=AuditAction.CREATE,
            description=f"Document {document.title} created successfully.",
            metadata={
                "document_id": str(document.id),
            },
        )
        return document

    @staticmethod
    @transaction.atomic
    def upload_new_version(*, document, request, owner, validated_data):
        latest_version = (DocumentVersion.objects.filter(document=document).order_by("-version_number").first())
        new_version = 1 if latest_version is None else latest_version.version_number + 1
        version = DocumentVersion.objects.create(
            document = document,
            version_number = new_version,
            file = validated_data["file"],
            uploaded_by=owner,
            notes=validated_data.get("notes", "")
        )

        AuditService.log(
            user=owner,
            request=request,
            action=AuditAction.UPDATE,
            description=f"uploaded version {new_version} for {document.title}.",
            metadata={
                "document_id":str(document.id),
                "version": new_version,
            },
        )
        return version

