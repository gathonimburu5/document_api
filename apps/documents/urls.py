from django.urls import path
from .views import (
    DocumentListAPIView,
    DocumentDetailAPIView,
    DocumentVersionAPIView,
    UploadDocumentVersionAPIView,
    DocumentVersionDetailAPIView,
    ArchiveDocumentAPIView,
    ApproveDocumentAPIView,
    SubmitDocumentAPIView,
    RestoreDocumentAPIView,
    RejectDocumentAPIView,
    DocumentCreateAPIView,
    DocumentUpdateAPIView,
)

urlpatterns = [
    path("list/", DocumentListAPIView.as_view(), name="document-list"),
    path("create/", DocumentCreateAPIView.as_view(), name="document-create"),
    path("<uuid:document_id>/", DocumentDetailAPIView.as_view(), name="document-detail"),
    path("<uuid:document_id>/update/", DocumentUpdateAPIView.as_view(), name="document-update"),
    path("versions/", DocumentVersionAPIView.as_view(), name="document-version-list",),
    path("versions/<int:version_id>/", DocumentVersionDetailAPIView.as_view(), name="document-version-detail"),
    path("<uuid:document_id>/versions/", UploadDocumentVersionAPIView.as_view(), name="document-version-upload"),
    path("<uuid:document_id>/submit/", SubmitDocumentAPIView.as_view(), name="document-submit"),
    path("<uuid:document_id>/approve/", ApproveDocumentAPIView.as_view(), name="document-approve"),
    path("<uuid:document_id>/reject/", RejectDocumentAPIView.as_view(), name="document-reject"),
    path("<uuid:document_id>/archive/", ArchiveDocumentAPIView.as_view(), name="document-archive"),
    path("<uuid:document_id>/restore/", RestoreDocumentAPIView.as_view(), name="document-restore"),
]
