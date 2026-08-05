from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Document, DocumentVersion
from .serializers import (DocumentVersionSerializer, UserSummarySerializer, DocumentSerializer, DocumentCreateSerializer, DocumentVersionCreateSerializer)
from services.document_service import DocumentService
from drf_spectacular.utils import extend_schema
from apps.commons.responses import CustomResponse

class CreateDocument(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser]

    @extend_schema(
        request=DocumentCreateSerializer,
        responses={201: DocumentSerializer, 400: "Bad Request"},
        description="Create document.",
        tags=["Documents"]
    )
    def post(self, request):
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = DocumentService.create_document(owner=request.user, request=request, validated_data=serializer.validated_data)
        response_document = DocumentSerializer(document)
        return CustomResponse.success(data=response_document.data, message="document successfully created", status=status.HTTP_201_CREATED)

class DocumentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Documents"],
        responses={200: DocumentSerializer(many=True)}
    )
    def get(self, request):
        documents = (Document.objects.filter(owner=request.user).prefetch_related("versions"))
        serializer = DocumentSerializer(documents, many=True)
        return CustomResponse.success(data=serializer.data, message="Document retrieved successfully.")

class DocumentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Document"],
        responses={200: DocumentSerializer},
    )
    def get(self, request, document_id):
        document = Document.objects.filter(id=document_id).prefetch_related("versions")
        serializer = DocumentSerializer(document)
        return CustomResponse.success(data=serializer.data, message="Document retrieved successfully.")

