from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from apps.commons.responses import CustomResponse
from django.shortcuts import get_object_or_404
from services.reviews_service import ReviewService
from .models import ReviewRequest, ReviewAssignment, Comment, ReviewDecision
from .serializers import (
    ReviewDecisionSerializer,
    ReviewAssignmentSerializer,
    CommentSerializer,
    ReviewRequestListSearializer,
    ReviewRequestDetailSerializer,
    ReviewRequestCreateSerializer,
    ReviewAssignmentCreateSerializer,
    ReviewDecisionCreateSerializer,
)

class ReviewRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ReviewRequestListSearializer(many=True)},
        description="Document review list.",
        operation_id="review_list"
    )
    def get(self, request):
        reviews = (ReviewRequest.objects.with_details().filter(requester=request.user).order_by("-created_at"))
        serializer = ReviewRequestListSearializer(reviews, many=True)
        return CustomResponse.success(message="review retrieved successfully.", data=serializer.data, status=status.HTTP_200_OK)

class ReviewRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser]

    @extend_schema(
        request=ReviewRequestCreateSerializer,
        responses={201: ReviewRequestDetailSerializer, 404: "Bad Request"},
        description="Create document review.",
        operation_id="review_create"
    )
    def post(self, request):
        serializer = ReviewRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review_request = ReviewService.create_review_request(
            requester=request.user,
            request=request,
            document=serializer.validated_data["document"],
            version=serializer.validated_data["version"],
            due_date=serializer.validated_data["due_date"]
        )
        response_serializer = ReviewRequestDetailSerializer(review_request)
        return CustomResponse.success(message="Review request created successfully", data=response_serializer.data, status=status.HTTP_201_CREATED)

class ReviewRequestDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ReviewRequestDetailSerializer, 404: "Bad Request"},
        description="Document review details.",
        operation_id="review_details"
    )
    def get(self, request, pk):
        review_request = get_object_or_404(ReviewRequest.objects.with_details(), pk=pk)
        serializer = ReviewRequestDetailSerializer(review_request)
        return CustomResponse.success(message="Review request retrieved successfully.", data=serializer.data, status=status.HTTP_200_OK)

class ReviewRequestSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ReviewRequestDetailSerializer, 404: "Bad Request"},
        description="document review submitted.", operation_id="review_submitted"
    )
    def post(self, request, pk):
        review_request = get_object_or_404(ReviewRequest, pk=pk, requester=request.user)
        review_request = ReviewService.submit_review_request(review_request=review_request, request=request)
        serializer = ReviewRequestDetailSerializer(review_request)
        return CustomResponse.success(message="Review request submitted successfully.", data=serializer.data, status=status.HTTP_200_OK)

class ReviewAssignmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ReviewAssignmentCreateSerializer,
        responses={201: ReviewAssignmentSerializer, 404: "Bad Request"},
        description="document review assignment.", operation_id="review_assignment"
    )
    def post(self, request, pk):
        review_request = get_object_or_404(ReviewRequest, pk=pk, requester=request.user)
        serializer = ReviewAssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignments = ReviewService.create_review_assignment(
            request_review=review_request, reviewers=serializer.validated_data["reviewers"], request=request
        )
        response_serializer = ReviewAssignmentSerializer(assignments, many=True)
        return CustomResponse.success(message="Reviews assigned successfully.", data=response_serializer.data, status=status.HTTP_201_CREATED)

class ReviewStartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ReviewRequestDetailSerializer, 404: "Bad Request"}, operation_id="review_start")
    def post(self, request, pk):
        review_request = get_object_or_404(ReviewRequest, pk=pk)
        review_request = ReviewService.start_review(review_request=review_request, request=request)
        serializer = ReviewRequestDetailSerializer(review_request)
        return CustomResponse.success(message="Review started successfully.", data=serializer.data, status=status.HTTP_200_OK)

class ReviewDecisionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ReviewDecisionCreateSerializer,
        responses={201: ReviewDecisionSerializer, 404: "Bad Request"},
        operation_id="review_decision"
    )
    def post(self, request, assignment_id):
        assignment = get_object_or_404(ReviewAssignment.objects.select_related("review", "reviewer"), pk=assignment_id, reviewer=request.user)
        serializer = ReviewDecisionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = ReviewService.create_review_decision(
            request=request,
            assignment=assignment,
            reviewer=request.user,
            decision=serializer.validated_data["decision"],
            comment=serializer.validated_data.get("comment", ""),
        )
        response_serializer = ReviewDecisionSerializer(decision)
        return CustomResponse.success(message="Review decision recorded successfully.", data=response_serializer.data, status=status.HTTP_201_CREATED)

class ReviewCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=CommentSerializer,
        responses={201: CommentSerializer, 404: "Bad Request"},
        operation_id="review_comment"
    )
    def post(self, request, pk):
        review_request = get_object_or_404(ReviewRequest, pk=pk)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = ReviewService.create_review_comment(
            request=request,
            review_request=review_request,
            author=request.user,
            content=serializer.validated_data["content"],
            parent=serializer.validated_data.get("parent"),
        )
        response_serializer = CommentSerializer(comment)
        return CustomResponse.success(message="Review comment created successfully.", data=response_serializer.data, status=status.HTTP_201_CREATED)


