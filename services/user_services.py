from apps.accounts.models import User, Role
from django.db import transaction
from apps.audits.models import AuditAction
from .audit_services import AuditService
import os

class UserService:
    @staticmethod
    @transaction.atomic
    def register_user(request, validated_data):
        """ Registers a new user with the provided validated data. """
        data = validated_data.copy()
        password = data.pop("password", None)
        data.pop("password_confirm", None)
        user = User.objects.create_user(password=password, **data)
        # Additional logic can be added here, such as sending a welcome email
        AuditService.log(user=user, request=request, action=AuditAction.USER_REGISTER, description=f"user registered successfully.")
        return user

class AdminService:
    @staticmethod
    @transaction.atomic
    def create_user(request, validated_data):
        """ Creates a new user with the provided validated data. """
        data = validated_data.copy()
        password = data.pop("password", None)
        data.pop("password_confirm", None)
        user = User.objects.create_user(password=password, **data)
        # Additional logic can be added here, such as sending a welcome email
        AuditService.log(user=user, request=request, action=AuditAction.USER_CREATE, description=f"user successfully created.")
        return user

    @staticmethod
    @transaction.atomic
    def update_user(user, request, validated_data):
        """ Updates an existing user with the provided validated data. """
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        AuditService.log(user=user, request=request, action=AuditAction.USER_UPDATE, description=f"user successfully updated.")
        return user

    @staticmethod
    @transaction.atomic
    def deactivate_user(request, user):
        """ Deactivates the specified user. """
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.USER_DEACTIVATE,
            description=f"User successfully deactivated {user.email}.",
            metadata={
                "target_user_id":user.id,
                "operation":"DEACTIVATED"
            }
        )
        return user

    @staticmethod
    @transaction.atomic
    def activate_user(request, user):
        """ Activates the specified user. """
        user.is_active = True
        user.save(update_fields=["is_active", "updated_at"])
        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.USER_ACTIVATE,
            description=f"User successfully activated {user.email}.",
            metadata={
                "target_user_id":user.id,
                "operations":"ACTIVATED"
            }
        )
        return user

    @staticmethod
    @transaction.atomic
    def lock_user(request, user):
        """ Locks the specified user. """
        user.is_locked = True
        user.is_active = False
        user.save(update_fields=["is_locked", "is_active", "updated_at"])
        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.USER_LOCK,
            description=f"User successfully locked {user.email}.",
            metadata={
                "target_user_id":user.id,
                "operation":"LOCKED"
            }
        )
        return user

    @staticmethod
    @transaction.atomic
    def unlock_user(request, user):
        """ Unlocks the specified user. """
        user.is_locked = False
        user.is_active = True
        user.failed_login_attempts = 0
        user.save(update_fields=["is_locked", "is_active", "failed_login_attempts", "updated_at"])
        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.USER_UNLOCK,
            description=f"User successfully unlocked {user.email}.",
            metadata={
                "target_user_id":user.id,
                "operation":"UNLOCKED"
            }
        )
        return user

    @staticmethod
    @transaction.atomic
    def soft_delete_user(request, user):
        """ Soft deletes the specified user. """
        user.is_deleted = True
        user.is_active = False
        user.save(update_fields=["is_deleted", "is_active", "updated_at"])
        AuditService.log(
            user=user,
            request=request,
            action=AuditAction.USER_SOFT_DELETE,
            description=f"User successfully soft deleted {user.email}.",
            metadata={
                "target_user_id":user.id,
                "operation":"DELETED"
            }
        )
        return user

class RoleService:
    @staticmethod
    @transaction.atomic
    def create_role(request, validated_data):
        """ Creates a new role with the provided validated data. """
        role = Role.objects.create(**validated_data)
        return role

    @staticmethod
    @transaction.atomic
    def update_role(role, request, validated_data):
        """ Updates an existing role with the provided validated data. """
        for attr, value in validated_data.items():
            setattr(role, attr, value)
        role.save()
        AuditService.log(user=request.user, request=request, action=AuditAction.ROLE_UPDATE, description=f"Role {role.name} updated.")
        return role

    @staticmethod
    @transaction.atomic
    def delete_role(request, role):
        """ Deletes the specified role. """
        if role.is_system:
            raise ValueError("System roles cannot be deleted.")
        role.delete()
        AuditService.log(user=request.user, request=request, action=AuditAction.ROLE_DELETE, description=f"Role {role.name} deleted.")
        return role

    @staticmethod
    @transaction.atomic
    def assign_role(request, user, role):
        """ Assigns the specified role to the user. """
        if not role.is_active:
            raise ValueError("Cannot assign an inactive role.")
        user.roles.add(role)
        AuditService.log(user=request.user, request=request, action=AuditAction.ROLE_ASSIGN, description=f"Role {role.name} assigned to user {user.email}.")
        return user

    @staticmethod
    @transaction.atomic
    def remove_role(request, user, role):
        """ Removes the specified role from the user. """
        user.roles.remove(role)
        AuditService.log(user=request.user, request=request, action=AuditAction.ROLE_REMOVE, description=f"Role {role.name} removed from user {user.email}.")
        return user

    @staticmethod
    @transaction.atomic
    def deactivate_role(request, role):
        """ Deactivates the specified role. """
        role.is_active = False
        role.save(update_fields=["is_active", "updated_at"])
        AuditService.log(user=request.user, request=request, action=AuditAction.ROLE_DEACTIVATE, description=f"Role {role.name} deactivated.")
        return role

    @staticmethod
    @transaction.atomic
    def activate_role(request, role):
        """ Activates the specified role. """
        role.is_active = True
        role.save(update_fields=["is_active", "updated_at"])
        AuditService.log(user=request.user, request=request, action=AuditAction.ROLE_ACTIVATE, description=f"Role {role.name} activated.")
        return role

class ProfileService:
    @staticmethod
    @transaction.atomic
    def update_profile(user, request, validated_data):
        """ Updates the profile of the specified user. """
        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()
        AuditService.log(user=user, request=request, action=AuditAction.PROFILE_UPDATE, description=f"User {user.email} updated their profile.")
        return user

    @staticmethod
    @transaction.atomic
    def upload_photo(user, request, validated_data):
        """ Uploads a profile picture for the specified user. """
        if user.profile_picture:
            if os.path.isfile(user.profile_picture.path):
                os.remove(user.profile_picture.path)

        user.profile_picture = validated_data["profile_picture"]
        user.save(update_fields=["profile_picture", "updated_at"])

        AuditService.log(user=user, request=request, action=AuditAction.PROFILE_PICTURE_UPLOAD, description=f"User {user.email} uploaded a new profile picture.")
        return user

    @staticmethod
    @transaction.atomic
    def remove_photo(user, request):
        """ Removes the profile picture of the specified user. """
        if user.profile_picture:
            if os.path.isfile(user.profile_picture.path):
                os.remove(user.profile_picture.path)
            user.profile_picture = None
            user.save(update_fields=["profile_picture", "updated_at"])
        AuditService.log(user=user, request=request, action=AuditAction.PROFILE_PICTURE_REMOVE, description=f"User {user.email} removed their profile picture.")
        return user

class PasswordService:
    @staticmethod
    @transaction.atomic
    def change_password(user, request, old_password, new_password):
        """ Changes the password of the specified user. """
        if not user.check_password(old_password):
            raise ValueError({ "old_password":"Old password is incorrect." })
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        AuditService.log(user=user, request=request, action=AuditAction.PASSWORD_CHANGE, description=f"User {user.email} changed their password.")
        return user
