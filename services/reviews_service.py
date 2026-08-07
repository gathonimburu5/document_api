from apps.reviews.models import ReviewRequest, ReviewAssignment, Comment, ReviewDecision, ReviewStatusChoices, ReviewDecisionChoices, ReviewAssignmentStatus
from django.db import transaction
from apps.audits.models import AuditAction
from .audit_services import AuditService
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import os

class ReviewService:

    @staticmethod
    @transaction.atomic
    def create_review_request(*, requester, document, version, due_date):
        if version.document_id != document.id:
            raise ValidationError({ "document-version": "The selected document version does not belong to this document." })
        if document.owner_id != requester.id:
            raise ValidationError({ "document":"You do not have permission to request a review for this document." })
        existing_request = ReviewRequest.objects.filter(document=document, version=version, requester=requester, status__in=[
            ReviewStatusChoices.DRAFT, ReviewStatusChoices.SUBMITTED, ReviewStatusChoices.IN_REVIEW
        ],).first()

        if existing_request:
            raise ValidationError({ "review_request":"An active review request already exists for this document version." })

        return ReviewRequest.objects.create(document=document, version=version, requester=requester, status=ReviewStatusChoices.DRAFT, due_date=due_date,)

    @staticmethod
    @transaction.atomic
    def create_review_assignment(*, reviewer, request_review):
        if request_review.status not in [ReviewStatusChoices.DRAFT, ReviewStatusChoices.SUBMITTED, ReviewStatusChoices.IN_REVIEW]:
            raise ValidationError({ "review_request":"This review request cannot receive a new assignment." })
        existing_assignment = ReviewAssignment.objects.filter(request_review=request_review, reviewer=reviewer).first()
        if existing_assignment:
            raise ValidationError({ "reviewer":"This reviewer is already assigned to this review request." })
        assignment = ReviewAssignment.objects.create(
            request_review=request_review, reviewer=reviewer
        )
        if request_review.status == ReviewStatusChoices.DRAFT:
            request_review.status = ReviewStatusChoices.IN_REVIEW
            request_review.save(update_fields=["status"])

        return assignment


