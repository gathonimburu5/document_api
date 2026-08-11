from rest_framework import serializers
from .models import ReviewRequest, ReviewAssignment, Comment, ReviewDecision, ReviewDecisionChoices
from apps.accounts.models import User
from apps.documents.models import Document, DocumentVersion

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name",)
class ReviewDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewDecision
        fields = ("decision", "comment", "created_at",)
        read_only_fields = ("created_at",)
class ReviewAssignmentSerializer(serializers.ModelSerializer):
    reviewer = UserSummarySerializer(read_only=True)
    decision = ReviewDecisionSerializer(read_only=True)

    class Meta:
        model = ReviewAssignment
        fields = ("id", "reviewer", "decision", "assigned_at", "status",)
        read_only_fields = ("id", "reviewer", "decision", "assigned_at", "status",)
class CommentSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "replies", "author", "parent", "content", "created_at", "updated_at", "is_resolved",)
        read_only_fields = ("id", "author", "created_at", "updated_at", "replies",)

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data
class ReviewDocumentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ("id", "title", "status")
class ReviewRequestListSearializer(serializers.ModelSerializer):
    document = ReviewDocumentSummarySerializer(read_only=True)
    requester = UserSummarySerializer(read_only=True)
    version_number = serializers.IntegerField(source="version.version_number", read_only=True)

    class Meta:
        model = ReviewRequest
        fields = ("id", "document", "version_number", "requester", "status", "due_date", "created_at", "updated_at",)
class ReviewRequestDetailSerializer(serializers.ModelSerializer):
    document = ReviewDocumentSummarySerializer(read_only=True)
    requester = UserSummarySerializer(read_only=True)
    assignments = ReviewAssignmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = ReviewRequest
        fields = ("id", "document", "version", "requester", "status", "due_date", "created_at", "updated_at", "assignments", "comments",)
        read_only_fields = ("id", "requester", "status", "created_at", "updated_at", "assignments", "comments",)
class ReviewRequestCreateSerializer(serializers.Serializer):
    document_id = serializers.UUIDField()
    version_id = serializers.IntegerField()
    due_date = serializers.DateTimeField(required=False, allow_null=True)

    # reviewer_ids = serializers.ListField(child=serializers.UUIDField(), allow_null=False)

    def validate(self, attrs):
        document_id = attrs["document_id"]
        version_id = attrs["version_id"]

        try:
            document = Document.objects.get(id=document_id, is_archived=False)
        except Document.DoesNotExist:
            raise serializers.ValidationError({ "document_id":"Document not found." })

        try:
            version = DocumentVersion.objects.get(id=version_id, document=document)
        except DocumentVersion.DoesNotExist:
            raise serializers.ValidationError({ "version_id":"The selected version does not belong to this document." })

        attrs["document"] = document
        attrs["version"] = version

        return attrs
class ReviewAssignmentCreateSerializer(serializers.Serializer):
    reviewer_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def validate(self, attrs):
        reviewer_ids = attrs["reviewer_ids"]
        if len(reviewer_ids) != len(set(reviewer_ids)):
            raise serializers.ValidationError({ "reviewer_ids":"Duplicate reviewers are not allowed." })
        reviewers  = User.objects.filter(id__in=reviewer_ids, is_active=True,)
        reviewer_map = { user.id: user for user in reviewers }

        # found_ids = set(users.values_list("id", flat=True))
        # requested_ids = set(value)

        missing_ids = [reviewer_id for reviewer_id in reviewer_ids if reviewer_id not in reviewer_map]
        if missing_ids:
            raise serializers.ValidationError({ "reviewer_ids":f"Invalid or inactive reviewer(s): {missing_ids}" })
        attrs["reviewers"] = [reviewer_map[reviewer_id] for reviewer_id in reviewer_ids]
        return attrs
class ReviewDecisionCreateSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=ReviewDecisionChoices.choices)
    comment = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        decision = attrs.get("decision")
        comment = attrs.get("comment", "").strip()

        if decision in (ReviewDecisionChoices.REJECT, ReviewDecisionChoices.REQUEST_CHANGES,) and not comment:
            raise serializers.ValidationError({ "comment":"A comment is required when rejecting or requesting changes." })

        attrs["comment"] = comment

        return attrs
