from rest_framework_simplejwt.tokens import RefreshToken
from .audit_services import AuditService
from apps.audits.models import AuditAction

class AuthService:
    @staticmethod
    def login(request, user):
        """ Generates JWT tokens for the authenticated user. """
        refresh = RefreshToken.for_user(user)
        AuditService.log( user=user, request=request, action=AuditAction.LOGIN, description=f"User {user.email} logged in." )
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "gender": user.gender,
                "address": user.address,
                "date_of_birth": user.date_of_birth,
                "profile_picture": user.profile_picture.url if user.profile_picture else None,
            },
        }

    @staticmethod
    def logout(request, refresh_token):
        """ Blacklists the provided refresh token. """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            AuditService.log( user=request.user, request=request, action=AuditAction.LOGOUT, description=f"User {request.user.email} logged out." )
        except Exception as e:
            raise ValueError("Invalid token or token already blacklisted.")