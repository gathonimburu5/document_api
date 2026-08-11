from django.db import models
from django.conf import settings

class AuditAction(models.TextChoices):
    CREATE = 'CREATE', 'Create'
    UPDATE = 'UPDATE', 'Update'
    DELETE = 'DELETE', 'Delete'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    SUBMITTED = 'SUBMITTED', 'Submitted'
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    IS_ARCHIVED = 'IS_ARCHIVED', 'Is Archived'
    RESTORED = 'RESTORED', 'Restored'
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'
    ASSIGN_ROLE = 'ASSIGN_ROLE', 'Assign Role'
    REMOVE_ROLE = 'REMOVE_ROLE', 'Remove Role'
    PASSWORD_CHANGE = 'PASSWORD_CHANGE', 'Password Change'
    PROFILE_UPDATE = 'PROFILE_UPDATE', 'Profile Update'
    PROFILE_PICTURE_UPLOAD = 'PROFILE_PICTURE_UPLOAD', 'Profile Picture Upload'
    PROFILE_PICTURE_REMOVE = 'PROFILE_PICTURE_REMOVE', 'Profile Picture Remove'
    ROLE_ACTIVATE = 'ROLE_ACTIVATE', 'Role Activate'
    ROLE_DEACTIVATE = 'ROLE_DEACTIVATE', 'Role Deactivate'
    USER_REGISTER = 'USER_REGISTER', 'User Register'
    USER_CREATE = 'USER_CREATE', 'User Create'
    USER_UPDATE = 'USER_UPDATE', 'User Update'
    USER_DEACTIVATE = 'USER_DEACTIVATE', 'User Deactivate'
    USER_ACTIVATE = 'USER_ACTIVATE', 'User Activate'
    USER_LOCK = 'USER_LOCK', 'User Lock'
    USER_UNLOCK = 'USER_UNLOCK', 'User Unlock'
    USER_SOFT_DELETE = 'USER_SOFT_DELETE', 'User Soft Delete'
    CREATE_REVIEW_REQUEST = 'CREATE_REVIEW_REQUEST', 'Create Review Request'
    SUBMIT_REVIEW_REQUEST = 'SUBMIT_REVIEW_REQUEST', 'Submit Review Request'
    CREATE_REVIEW_ASSIGNMENT = 'CREATE_REVIEW_ASSIGNMENT', 'Create Review Assignment'
    START_REVIEW = 'START_REVIEW', 'Start Review'
    CREATE_REVIEW_DECISION = 'CREATE_REVIEW_DECISION', 'Create Review Decision'
    CREATE_REVIEW_COMMENT = 'CREATE_REVIEW_COMMENT', 'Create Review Comment'
    REVIEW_APPROVED = 'REVIEW_APPROVED', 'Review Approved'
    REVIEW_REJECTED = 'REVIEW_REJECTED', 'Review Rejected'
    REVIEW_CHANGES = 'REVIEW_CHANGES', 'Review Changes'

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs")
    action = models.CharField(max_length=255, choices=AuditAction.choices)
    description = models.TextField(blank=True, null=True)
    method = models.CharField(max_length=10, blank=True)
    endpoint = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.created_at}"