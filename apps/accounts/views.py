from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Role
from .serializers import (
    RegisterUserSerializer,
    UserSerializer,
    CurrentUserSerializer,
    LoginSerializer,
    LogoutSerializer,
    RoleSerializer,
    RoleCreateSerializer,
    RoleUpdateSerializer,
    AssignRoleSerializer,
    RemoveRoleSerializer,
    UserListSerializer,
    UserDetailSerializer,
    AdminCreateUserSerializer,
    AdminUpdateUserSerializer,
    ProfileSerializer,
    UpdateProfileSerializer,
    UploadProfilePictureSerializer,
    ChangePasswordSerializer,
)
from services.user_services import (
    UserService,
    AdminService,
    RoleService,
    ProfileService,
    PasswordService,
)
from services.authe_services import AuthService
from drf_spectacular.utils import extend_schema
from apps.commons.responses import CustomResponse


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [FormParser]

    @extend_schema(
        request=RegisterUserSerializer,
        responses={201: UserSerializer, 400: "Bad Request"},
        description="Register a new user.",
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.register_user(request, serializer.validated_data)
        response_serializer = UserSerializer(user)
        return CustomResponse.success(data=response_serializer.data, message="User registered successfully.", status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: "Login successful", 400: "Bad Request"},
        description="Authenticate a user and return JWT tokens.",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = AuthService.login(request, user)
        return CustomResponse.success(data=tokens, message="Login successful.", status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={200: "Logout successful", 400: "Bad Request"},
        description="Logout a user by blacklisting the refresh token.",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        AuthService.logout(request, refresh_token)
        return CustomResponse.success(message="Logout successful.", status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CurrentUserSerializer, 401: "Unauthorized"},
        description="Retrieve the currently authenticated user's details.",
    )
    def get(self, request):
        user = request.user
        serializer = CurrentUserSerializer(user)
        return CustomResponse.success(data=serializer.data, message="Current user retrieved successfully.", status=status.HTTP_200_OK)

class RoleListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: RoleSerializer(many=True), 401: "Unauthorized"},
        operation_id="list_roles",
        description="Retrieve a list of all roles.",
    )
    def get(self, request):
        roles = Role.objects.filter(is_active=True).order_by("priority").all()
        serializer = RoleSerializer(roles, many=True)
        return CustomResponse.success(data=serializer.data, message="Roles retrieved successfully.", status=status.HTTP_200_OK)

    @extend_schema(
        request=RoleCreateSerializer,
        responses={201: RoleSerializer, 400: "Bad Request"},
        operation_id="create_role",
        description="Create a new role.",
    )
    def post(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = RoleService.create_role(request, serializer.validated_data)
        response_serializer = RoleSerializer(role)
        return CustomResponse.success(data=response_serializer.data, message="Role created successfully.", status=status.HTTP_201_CREATED)

class RoleDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, role_id):
        return Role.objects.filter(id=role_id).first()

    @extend_schema(
        responses={200: RoleSerializer, 404: "Not Found"},
        operation_id="retrieve_role",
        description="Retrieve details of a specific role by ID.",
    )
    def get(self, request, role_id):
        role = self.get_object(role_id)
        if not role:
            return CustomResponse.error(message="Role not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role)
        return CustomResponse.success(data=serializer.data, message="Role retrieved successfully.", status=status.HTTP_200_OK)

    @extend_schema(
        request=RoleUpdateSerializer,
        responses={200: RoleSerializer, 400: "Bad Request", 404: "Not Found"},
        operation_id="update_role",
        description="Update an existing role by ID.",
    )
    def put(self, request, role_id):
        role = self.get_object(role_id)
        if not role:
            return CustomResponse.error(message="Role not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_role = RoleService.update_role(role, request, serializer.validated_data)
        response_serializer = RoleSerializer(updated_role)
        return CustomResponse.success(data=response_serializer.data, message="Role updated successfully.", status=status.HTTP_200_OK)

    @extend_schema(
        responses={204: "No Content", 404: "Not Found"},
        operation_id="delete_role",
        description="Delete a specific role by ID.",
    )
    def delete(self, request, role_id):
        role = self.get_object(role_id)
        if not role:
            return CustomResponse.error(message="Role not found.", status=status.HTTP_404_NOT_FOUND)
        RoleService.delete_role(request, role)
        return CustomResponse.success(message="Role deleted successfully.", status=status.HTTP_204_NO_CONTENT)

class AssignRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AssignRoleSerializer,
        responses={200: "Role assigned successfully", 400: "Bad Request", 404: "Not Found"},
        operation_id="assign_role",
        description="Assign a role to a user.",
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data["role"]
        AdminService.assign_role(request, user, role)
        return CustomResponse.success(message=f"Role '{role.name}' assigned to user '{user.email}' successfully.", status=status.HTTP_200_OK)

class RemoveRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RemoveRoleSerializer,
        responses={200: "Role removed successfully", 400: "Bad Request", 404: "Not Found"},
        operation_id="remove_role",
        description="Remove a role from a user.",
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, is_deleted=True).first()
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = RemoveRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data["role"]
        AdminService.remove_role(request, user, role)
        return CustomResponse.success(message=f"Role '{role.name}' removed from user '{user.email}' successfully.", status=status.HTTP_200_OK)

class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserListSerializer(many=True), 401: "Unauthorized"},
        operation_id="list_users",
        description="Retrieve a list of all users.",
    )
    def get(self, request):
        users = User.objects.filter(is_deleted=False).prefetch_related("roles").all()
        serializer = UserListSerializer(users, many=True)
        return CustomResponse.success(data=serializer.data, message="Users retrieved successfully.", status=status.HTTP_200_OK)

    @extend_schema(
        request=AdminCreateUserSerializer,
        responses={201: UserDetailSerializer, 400: "Bad Request"},
        operation_id="create_user",
        description="Create a new user.",
    )
    def post(self, request):
        serializer = AdminCreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AdminService.create_user(request, serializer.validated_data)
        response_serializer = UserDetailSerializer(user)
        return CustomResponse.success(data=response_serializer.data, message="User created successfully.", status=status.HTTP_201_CREATED)

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        return User.objects.filter(id=user_id, is_deleted=False).prefetch_related("roles").first()

    @extend_schema(
        responses={200: UserDetailSerializer, 404: "Not Found"},
        operation_id="retrieve_user",
        description="Retrieve details of a specific user by ID.",
    )
    def get(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = UserDetailSerializer(user)
        return CustomResponse.success(data=serializer.data, message="User retrieved successfully.", status=status.HTTP_200_OK)

    @extend_schema(
        request=AdminUpdateUserSerializer,
        responses={200: UserDetailSerializer, 400: "Bad Request", 404: "Not Found"},
        operation_id="update_user",
        description="Update an existing user by ID.",
    )
    def put(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_user = AdminService.update_user(request, user, serializer.validated_data)
        response_serializer = UserDetailSerializer(updated_user)
        return CustomResponse.success(data=response_serializer.data, message="User updated successfully.", status=status.HTTP_200_OK)

    @extend_schema(
        responses={204: "No Content", 404: "Not Found"},
        operation_id="delete_user",
        description="Soft delete a specific user by ID.",
    )
    def delete(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        AdminService.soft_delete_user(request, user)
        return CustomResponse.success(message="User soft deleted successfully.", status=status.HTTP_204_NO_CONTENT)

class DeactivateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "User deactivated successfully", 404: "Not Found"},
        operation_id="deactivate_user",
        description="Deactivate a specific user by ID.",
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        AdminService.deactivate_user(request, user)
        return CustomResponse.success(message="User deactivated successfully.", status=status.HTTP_200_OK)

class ActivateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "User activated successfully", 404: "Not Found"},
        operation_id="activate_user",
        description="Activate a specific user by ID.",
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        AdminService.activate_user(request, user)
        return CustomResponse.success(message="User activated successfully.", status=status.HTTP_200_OK)

class LockUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "User locked successfully", 404: "Not Found"},
        operation_id="lock_user",
        description="Lock a specific user by ID.",
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        AdminService.lock_user(request, user)
        return CustomResponse.success(message="User locked successfully.", status=status.HTTP_200_OK)

class UnlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "User unlocked successfully", 404: "Not Found"},
        operation_id="unlock_user",
        description="Unlock a specific user by ID.",
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            return CustomResponse.error(message="User not found.", status=status.HTTP_404_NOT_FOUND)
        AdminService.unlock_user(request, user)
        return CustomResponse.success(message="User unlocked successfully.", status=status.HTTP_200_OK)

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProfileSerializer, 401: "Unauthorized"},
        operation_id="retrieve_profile",
        description="Retrieve the profile of the currently authenticated user.",
    )
    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return CustomResponse.success(data=serializer.data, message="Profile retrieved successfully.", status=status.HTTP_200_OK)

class UpdateProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=UpdateProfileSerializer,
        responses={200: ProfileSerializer, 400: "Bad Request", 401: "Unauthorized"},
        operation_id="update_profile",
        description="Update the profile of the currently authenticated user.",
    )
    def put(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_user = ProfileService.update_profile(user, request, serializer.validated_data)
        response_serializer = ProfileSerializer(updated_user)
        return CustomResponse.success(data=response_serializer.data, message="Profile updated successfully.", status=status.HTTP_200_OK)

class UploadProfilePictureAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=UploadProfilePictureSerializer,
        responses={200: ProfileSerializer, 400: "Bad Request", 401: "Unauthorized"},
        operation_id="upload_profile_picture",
        description="Upload or update the profile picture of the currently authenticated user.",
    )
    def post(self, request):
        user = request.user
        serializer = UploadProfilePictureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_user = ProfileService.upload_photo(user, request, serializer.validated_data)
        response_serializer = ProfileSerializer(updated_user)
        return CustomResponse.success(data=response_serializer.data, message="Profile picture uploaded successfully.", status=status.HTTP_200_OK)

class RemoveProfilePictureAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProfileSerializer, 401: "Unauthorized"},
        operation_id="remove_profile_picture",
        description="Remove the profile picture of the currently authenticated user.",
    )
    def delete(self, request):
        user = request.user
        updated_user = ProfileService.remove_photo(user, request)
        response_serializer = ProfileSerializer(updated_user)
        return CustomResponse.success(data=response_serializer.data, message="Profile picture removed successfully.", status=status.HTTP_200_OK)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: "Password changed successfully", 400: "Bad Request", 401: "Unauthorized"},
        operation_id="change_password",
        description="Change the password of the currently authenticated user.",
    )
    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordService.change_password(user, request, serializer.validated_data["old_password"], serializer.validated_data["new_password"])
        return CustomResponse.success(message="Password changed successfully.", status=status.HTTP_200_OK)

