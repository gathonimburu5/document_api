from apps.reviews.models import ReviewRequest, ReviewAssignment, Comment, ReviewDecision, ReviewStatusChoices, ReviewDecisionChoices, ReviewAssignmentStatus
from django.db import transaction
from apps.audits.models import AuditAction
from .audit_services import AuditService
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import os

class ReviewService:
    @staticmethod
    def _update_review_status(review_request):
        assignments = review_request.assignments.all()
        if assignments.filter(status=ReviewAssignmentStatus.PENDING).exists():
            return
        if assignments.filter(status=ReviewAssignmentStatus.PENDING).exists():
            return

        decisions = ReviewDecision.objects.filter(assignment__review=review_request)
        if decisions.filter(decision=ReviewDecisionChoices.REJECT).exists():
            review_request.status = ReviewStatusChoices.REJECTED
        elif decisions.filter(decision=ReviewDecisionChoices.REQUEST_CHANGES).exists():
            review_request.status = ReviewStatusChoices.CHANGES_REQUESTED
        elif (decisions.exists() and not decisions.exclude(decision=ReviewDecisionChoices.APPROVE).exists()):
            review_request.status = ReviewStatusChoices.APPROVED
        else:
            return

        review_request.save(update_fields=["status", "updated_at"])

    @staticmethod
    @transaction.atomic
    def create_review_request(*, requester, request, document, version, due_date=None):
        if version.document_id != document.id:
            raise ValidationError({ "document-version": "The selected document version does not belong to this document." })
        if document.owner_id != requester.id:
            raise ValidationError({ "document":"You do not have permission to request a review for this document." })
        if due_date and due_date <= timezone.now():
            raise ValidationError({ "due_date":"The due date must be in the future." })
        existing_request = ReviewRequest.objects.filter(
            document=document,
            version=version,
            requester=requester,
            status__in=[
                ReviewStatusChoices.DRAFT, ReviewStatusChoices.SUBMITTED, ReviewStatusChoices.IN_REVIEW
            ],
        ).first()

        if existing_request:
            raise ValidationError({ "review_request":"An active review request already exists for this document version." })

        review = ReviewRequest.objects.create(document=document, version=version, requester=requester, status=ReviewStatusChoices.DRAFT, due_date=due_date,)

        AuditService.log(
            user=requester,
            request=request,
            action=AuditAction.CREATE_REVIEW_REQUEST,
            description=f"review request successfully created.",
            metadata={
                "review_status":review.status
            }
        )

        return review

    @staticmethod
    @transaction.atomic
    def submit_review_request(*, review_request):
        if review_request.status != ReviewStatusChoices.DRAFT:
            raise ValidationError({ "review_request":"Only draft review requests can be submitted." })
        review_request.status = ReviewStatusChoices.SUBMITTED
        review_request.save(update_fields=["status", "updated_at"])
        return review_request

    @staticmethod
    @transaction.atomic
    def create_review_assignment(*, request_review, reviewers,):
        if request_review.status != ReviewStatusChoices.SUBMITTED:
            raise ValidationError({ "review_request":"Reviewers can only be assigned to a submitted review request." })

        assignments = []
        for reviewer in reviewers:
            existing_assignment = ReviewAssignment.objects.filter(review=request_review, reviewer=reviewer).first()
            if existing_assignment:
                raise ValidationError({ "reviewer":f"{reviewer.email} is already assigned to this review request." })

            assignment = ReviewAssignment.objects.create(
                review=request_review,
                reviewer=reviewer,
                status=ReviewAssignmentStatus.PENDING,
            )

            assignments.append(assignment)

        return assignments

    @staticmethod
    @transaction.atomic
    def start_review(*, review_request):
        if review_request.status != ReviewStatusChoices.SUBMITTED:
            raise ValidationError({ "review_request":"Only submitted review requests can be started." })

        assignments = review_request.assignments.filter(status=ReviewAssignmentStatus.PENDING)
        if not assignments.exists():
            raise ValidationError({ "review_request":"At least one reviewer must be assigned before the review can be started." })

        now = timezone.now()

        assignments.update(status=ReviewAssignmentStatus.IN_REVIEW, started_at=now,)

        review_request.status = ReviewStatusChoices.IN_REVIEW
        review_request.save(update_fields=["status", "updated_at"])
        return review_request

    @staticmethod
    @transaction.atomic
    def create_review_decision(*, assignment, reviewer, decision, comment="",):
        if assignment.reviewer_id != reviewer.id:
            raise ValidationError({ "assignment":"You are not assigned to this review." })
        if assignment.status != ReviewAssignmentStatus.IN_REVIEW:
            raise ValidationError({ "assignment":"A decision can only be made for an assignment that is in review." })
        if hasattr(assignment, "decision"):
            raise ValidationError({ "decision":"A decision has already been recorded for this assignment." })
        if decision in [ReviewDecisionChoices.REJECT, ReviewDecisionChoices.REQUEST_CHANGES] and not comment.strip():
            raise ValidationError({ "comment":"A comment is required when rejecting or requesting changes." })
        review_decision = ReviewDecision.objects.create(
            assignment=assignment,
            decision=decision,
            comment=comment.strip(),
        )

        assignment.status = ReviewAssignmentStatus.COMPLETED
        assignment.completed_at = timezone.now()
        assignment.save(update_fields=["status", "completed_at"])

        ReviewService._update_review_status(assignment.review)

        return review_decision

    @staticmethod
    @transaction.atomic
    def create_review_comment(*, review_request, author, content, parent=None):
        if review_request.status not in [ReviewStatusChoices.IN_REVIEW, ReviewStatusChoices.CHANGES_REQUESTED, ReviewStatusChoices.APPROVED, ReviewStatusChoices.REJECTED]:
            raise ValidationError({ "review_request":"Comments cannot be added to a draft or unsubmitted review request." })
        if parent:
            if parent.review_id != review_request.id:
                raise ValidationError({ "parent":"The parent comment does not belong to this review." })

        content = content.strip()
        if not content:
            raise ValidationError({ "content":"Comment cannot be empty." })

        return Comment.objects.create(
            review=review_request,
            author=author,
            parent=parent,
            content=content
        )


