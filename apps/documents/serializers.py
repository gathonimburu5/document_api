from rest_framework import serializers
from .models import Document, DocumentVersion
from apps.accounts.models import User
from apps.commons.utils import validate_file_size, validate_upload_file

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name",)

class DocumentVersionSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_upload_file])
    uploaded_by = UserSummarySerializer(read_only=True)
    class Meta:
        model = DocumentVersion
        fields = ("id", "version_number", "file", "uploaded_by", "uploaded_at", "notes",)
        read_only_fields = ("version_number", "uploaded_by", "uploaded_at")

class DocumentListSerializer(serializers.ModelSerializer):
    owner = UserSummarySerializer(read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ("id", "title", "description", "status", "owner", "created_at", "is_archived", "updated_at", "latest_version",)

    def get_latest_version(self, obj):
        latest = obj.versions.first()
        if latest:
            return DocumentVersionSerializer(latest).data
        return None

class DocumentDetailSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)
    owner = UserSummarySerializer(read_only=True)
    class Meta:
        model = Document
        fields = ("title", "description", "status", "owner", "created_at", "is_archived", "updated_at", "versions",)

class DocumentCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(validators=[validate_upload_file])
    notes = serializers.CharField(required=False)

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title is too short.")
        return value

class DocumentUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Document
        fields = ("title", "description",)

class DocumentVersionCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_upload_file])
    notes = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = DocumentVersion
        fields = ("file", "notes")

class DocumentRejectSerializer(serializers.ModelSerializer):
    reject_reason = serializers.CharField(required=True)

    class Meta:
        model = Document
        fields = ("reject_reason",)