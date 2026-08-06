from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Document, DocumentVersion
from .serializers import (
    DocumentVersionSerializer,
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentCreateSerializer,
    DocumentVersionCreateSerializer,
    DocumentUpdateSerializer,
    DocumentRejectSerializer
)
from services.document_service import DocumentService
from drf_spectacular.utils import extend_schema
from apps.commons.responses import CustomResponse
from django.shortcuts import get_object_or_404

class DocumentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DocumentListSerializer(many=True)},
        description="List of documents available",
        operation_id="document_list"
    )
    def get(self, request):
        documents = (Document.objects.active().owned_by(request.user).with_details())
        # .filter(owner=request.user, is_archived=False,).select_related("owner").order_by("-updated_at").prefetch_related("versions", "versions__uploaded_by")
        serializer = DocumentListSerializer(documents, many=True)
        return CustomResponse.success(data=serializer.data, message="Document retrieved successfully.")
class DocumentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    @extend_schema(
        request=DocumentCreateSerializer,
        responses={201: DocumentDetailSerializer, 400: "Bad Request"},
        description="Create document.",
        operation_id="document_create"
    )
    def post(self, request):
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = DocumentService.create_document(owner=request.user, request=request, validated_data=serializer.validated_data)
        response_document = DocumentDetailSerializer(document)
        return CustomResponse.success(data=response_document.data, message="document successfully created", status=status.HTTP_201_CREATED)

class DocumentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_document(self, document_id, request):
        # .select_related("owner").prefetch_related("versions")  owner=request.user, is_archived=False
        return get_object_or_404(Document.objects.active().owned_by(request.user).with_details(), pk=document_id,)

    @extend_schema(
        responses={200: DocumentDetailSerializer, 404: "Bad Request"},
        description="document details",
        operation_id="document_detail"
    )
    def get(self, request, document_id):
        document = self.get_document(document_id, request)
        if not document:
            return CustomResponse.error(message="document not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentDetailSerializer(document)
        return CustomResponse.success(data=serializer.data, message="Document retrieved successfully.")

class DocumentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    @extend_schema(
        request=DocumentUpdateSerializer,
        responses={200: DocumentDetailSerializer, 404: "Bad Request"},
        description="document update",
        operation_id="document_update"
    )
    def patch(self, request, document_id):
        document = self.get_document(document_id, request)
        if not document:
            return CustomResponse.error(message="document not found.", status=status.HTTP_404_NOT_FOUND)
        serializer = DocumentUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.validated_data
        doc_update = DocumentService.update_document(document=document, user=request.user, request=request, validated_data=serializer_data)
        response_doc = DocumentDetailSerializer(doc_update)
        return CustomResponse.success(data=response_doc.data, message="document updated successfully.", status=status.HTTP_200_OK)

class DocumentVersionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DocumentVersionSerializer, 404: "No document version found."},
        description="document version list",
        operation_id="document_version"
    )
    def get(self, request):
        version = (DocumentVersion.objects.select_related("document", "uploaded_by").filter(uploaded_by=request.user).order_by("-uploaded_at"))
        serializer = DocumentVersionSerializer(version, many=True)
        return CustomResponse.success(data=serializer.data, message="Retrieved document versions.")

class UploadDocumentVersionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def get_document(self, document_id, request):
        return get_object_or_404(Document.objects.active().owned_by(request.user).with_details(), pk=document_id,)

    @extend_schema(
        request=DocumentVersionCreateSerializer,
        responses={200: DocumentVersionSerializer, 404: "Bad Request"},
        operation_id="upload_document_version",
        description="document version uploads"
    )
    def post(self, request, document_id):
        document = self.get_document(document_id, request)
        serializer = DocumentVersionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        version_upload = DocumentService.upload_new_version(document=document, request=request, owner=request.user, validated_data=serializer.validated_data)
        version_response = DocumentVersionSerializer(version_upload)
        return CustomResponse.success(data=version_response.data, message="document version uploaded successfully.", status=status.HTTP_200_OK)

class DocumentVersionDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DocumentVersionSerializer, 404: "Bad Request"},
        operation_id="document_version_details",
        description="document version details"
    )
    def get(self, request, version_id):
        version = get_object_or_404(DocumentVersion.objects.select_related("document", "uploaded_by"), pk=version_id, document__owner=request.user,)
        serializer = DocumentVersionSerializer(version)
        return CustomResponse.success(data=serializer.data, message="document version retrieved.")

class ArchiveDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "document archived", 404: "Not found"},
        operation_id="document_archived",
        description="document archived"
    )
    def post(self, request, document_id):
        document = get_object_or_404(Document.objects.active().owned_by(request.user).with_details(), pk=document_id,)
        DocumentService.archive_document(document=document, user=request.user, request=request)
        return CustomResponse.success(message="document archieved successfully.", status=status.HTTP_200_OK)

class ApproveDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "document approved", 404: "Bad Request"},
        operation_id="document_approved",
        description="document approve"
    )
    def post(self, request, document_id):
        document = get_object_or_404(Document.objects.active().owned_by(request.user).with_details(), pk=document_id,)
        DocumentService.approve_document(document=document, user=request.user, request=request)
        return CustomResponse.success(message="document approved successfully.", status=status.HTTP_200_OK)

class SubmitDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "document submitted", 404: "Bad Request"},
        operation_id="document_submited",
        description="document submitted"
    )
    def post(self, request, document_id):
        document = get_object_or_404(Document.objects.active().owned_by(request.user).with_details(), pk=document_id,)
        DocumentService.submit_document(document=document, user=request.user, request=request)
        return CustomResponse.success(message="document submitted successfully.", status=status.HTTP_200_OK)

class RestoreDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: "Document Restored", 404: "Bad Request"},
        operation_id="document_restored",
        description="document restored"
    )
    def post(self, request, document_id):
        document = get_object_or_404(Document.objects.archived().owned_by(request.user).with_details(), pk=document_id,)
        DocumentService.restore_document(document=document, user=request.user, request=request)
        return CustomResponse.success(message="document restored successfully.", status=status.HTTP_200_OK)

class RejectDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=DocumentRejectSerializer,
        responses={200: "document rejected", 404: "Bad Request"},
        operation_id="document_rejected",
        description="document rejected"
    )
    def post(self, request, document_id):
        document = get_object_or_404(Document.objects.active().owned_by(request.user).with_details(), pk=document_id,)
        serializer = DocumentRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        DocumentService.reject_document(document=document, user=request.user, request=request, validated_data=serializer.validated_data)
        return CustomResponse.success(message="document rejected successfully.", status=status.HTTP_200_OK)

