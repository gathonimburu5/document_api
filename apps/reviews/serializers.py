from rest_framework import serializers
from .models import ReviewRequest, ReviewAssignment, Comment, ReviewDecision

class ReviewAssignmentSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.get_full_name", read_only=True)

    class Meta:
        model = ReviewAssignment
        fields = ("id", "review", "reviewer", "reviewer_name", "assigned_at", "is_completed",)
        read_only_fields = ("assigned_at")

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "review", "author", "author_name", "parent", "content", "created_at", "updated_at", "is_resolved")
        read_only_fields = ("created_at", "updated_at")

class ReviewDecisionSerializer(serializers.ModelSerializer):
    review_name = serializers.CharField(source="reviewer.get_full_name", read_only=True)

    class Meta:
        model = ReviewDecision
        fields = ("id", "review", "reviewer", "review_name", "decision", "comment", "created_at")
        read_only_fields = ("created_at")

class ReviewRequestSearializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source="requester.get_full_name", read_only=True)
    assignments = ReviewAssignmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    decisions = ReviewDecisionSerializer(many=True, read_only=True)

    class Meta:
        model = ReviewRequest
        fields = ("id", "document", "version", "requester", "requester_name", "status", "due_date", "created_at", "updated_at", "assignments", "comments", "decisions")
        read_only_fields = ("created_at", "updated_at")

class CreateReviewRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRequest
        fields = ("document", "version", "due_date")

    def create(self, validated_data):
        validated_data["requester"] = self.context["request"].user
        validated_data["status"] = "SUBMITTED"

        return super().create(validated_data)
