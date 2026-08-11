from apps.notifications.models import Notification, NotificationTypeChoices
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils import timezone
import os

class NotificationService:
    @staticmethod
    @transaction.atomic
    def create_notification(*, recipient, notification_type, title, message, review=None):
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            review=review,
        )
        return notification

    @staticmethod
    @transaction.atomic
    def notify_review_assignment(*, reviewer, review,):
        return NotificationService.create_notification(
            recipient=reviewer,
            notification_type=(NotificationTypeChoices.REVIEW_ASSIGNED),
            title="Review Assigned",
            message=(
                f"You have been assigned to review "
                f"'{review.document.title}'."
            ),
            review=review
        )

    @staticmethod
    @transaction.atomic
    def notify_review_started(*, reviewer, review,):
        return NotificationService.create_notification(
            recipient=reviewer,
            notification_type=(NotificationTypeChoices.REVIEW_STARTED),
            title="Review Started",
            message=(
                f"The review for "
                f"'{review.document.title}' has started."
            ),
            review=review
        )

    @staticmethod
    @transaction.atomic
    def notify_decision_submitted(*, recipient, review, decision,):
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=(NotificationTypeChoices.DECISION_SUBMITTED),
            title="Review Decision Submitted",
            message=(
                f"A reviewer has submitted a "
                f"{decision.lower().replace("_", " ")} "
                f"decision for '{review.document.title}'."
            ),
            review=review,
        )

    @staticmethod
    @transaction.atomic
    def notify_review_approved(*, recipient, review,):
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=(NotificationTypeChoices.REVIEW_APPROVED),
            title="Review Approved",
            message=(
                f"Your review request for "
                f"'{review.document.title}' has been approved."
            ),
            review=review,
        )

    @staticmethod
    @transaction.atomic
    def notify_review_rejected(*, recipient, review,):
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=(NotificationTypeChoices.REVIEW_REJECTED),
            title="Review Rejected",
            message=(
                f"Your review request for "
                f"'{review.document.title}' has been rejected."
            ),
            review=review,
        )

    @staticmethod
    @transaction.atomic
    def notify_changes_requested(*, recipient, review,):
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=(NotificationTypeChoices.CHANGES_REQUESTED),
            title="Changes Requested",
            message=(
                f"Changes have been requested for "
                f"'{review.document.title}'."
            ),
            review=review,
        )

    @staticmethod
    @transaction.atomic
    def notify_comment_added(*, recipient, review, author,):
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=(NotificationTypeChoices.COMMENT_ADDED),
            title="New Review Comment",
            message=(
                f"{author.get_full_name() or author.email} "
                f"added a comment to "
                f"'{review.document.title}'."
            ),
            review=review,
        )