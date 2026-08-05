from rest_framework import serializers
from .models import Document, DocumentVersion
from apps.accounts.models import User

class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ("id", "version_number", "file", "uploaded_by", "uploaded_at", "notes",)
        read_only_fields = ("version_number", "uploaded_by", "uploaded_at")

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name",)

class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)
    owner = UserSummarySerializer(read_only=True)
    # owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Document
        fields = ("id", "title", "description", "owner", "created_at", "updated_at", "versions",)

class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("title", "description",)

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

class DocumentVersionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ("file", "notes")

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)