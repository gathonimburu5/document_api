from rest_framework import serializers
from .validators import validate_password_stregth
from .models import User, Role
from django.contrib.auth import authenticate
from apps.commons.utils import validate_file_size

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password_stregth])

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone_number", "gender", "date_of_birth", "address",)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "gender", "date_of_birth", "address", "profile_picture", "created_at")

class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "gender", "date_of_birth", "address", "profile_picture", "is_email_verified", "created_at")

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data["user"] = user
        return data

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "description", "priority", "is_system", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "is_system", "created_at", "updated_at")

class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("name", "description", "priority", "is_active")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Role name cannot be empty.")
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value

class RoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("name", "description", "priority", "is_active")

class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.filter(is_active=True), source="role")

class RemoveRoleSerializer(serializers.Serializer):
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source="role")

class UserListSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "gender", "date_of_birth", "address", "profile_picture", "is_email_verified", "is_locked", "is_deleted", "roles", "created_at")

    def get_roles(self, obj):
        return [role.name for role in obj.roles.all()]

class UserDetailSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone_number", "gender", "date_of_birth", "address", "profile_picture", "is_email_verified", "is_locked", "is_deleted", "roles", "created_at")

    def get_roles(self, obj):
        return [
            {
                "id": role.id,
                "name": role.name,
            }
            for role in obj.roles.all() if role.is_active
        ]

class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password_stregth])

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone_number", "gender", "date_of_birth", "address")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

class AdminUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "gender", "date_of_birth", "address")

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, validators=[validate_file_size])

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "gender", "date_of_birth", "address", "profile_picture")
        read_only_fields = ("email", "is_email_verified", "is_locked", "is_deleted", "created_at")

class UpdateProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, validators=[validate_file_size])

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "gender", "date_of_birth", "address", "profile_picture")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone_number": {"required": False},
            "gender": {"required": False},
            "date_of_birth": {"required": False},
            "address": {"required": False},
            "profile_picture": {"required": False},
        }

    def validate_phone_number(self, value):
        user = self.instance
        if value and User.objects.filter(phone_number=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

class UploadProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=True, validators=[validate_file_size])

    class Meta:
        model = User
        fields = ("profile_picture",)

    def validate_profile_picture(self, value):
        if not value:
            raise serializers.ValidationError("Profile picture is required.")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password_stregth])



