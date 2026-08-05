from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_roles(self, obj):
        return ", ".join(role.name for role in obj.role.all())

    get_roles.short_description = "Roles"

    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "get_roles",
        "is_active",
        "is_email_verified",
        "created_at",
    )
    list_filter = (
        "roles",
        "is_active",
        "is_email_verified",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "profile_picture",
                    "date_of_birth",
                    "gender",
                    "address",
                )
            },
        ),
        (
            "Application",
            {
                "fields": (
                    "roles",
                    "is_email_verified",
                    "failed_login_attempts",
                    "last_login_ip",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "roles",
                ),
            },
        ),
    )
