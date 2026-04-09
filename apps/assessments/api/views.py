from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.assessments.models import Assessment, Submission
from .serializers import AssessmentSerializer, SubmissionSerializer, CreateSubmissionSerializer
from apps.assessments.services import AssessmentService
from apps.core.mixins import AuditMixin


class AssessmentViewSet(AuditMixin, viewsets.ReadOnlyModelViewSet):
    """
    Read-only for students to view assessments.
    Instructors would have a separate management view/endpoint.
    """
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(
            lesson__module__course__is_published=True
        ).prefetch_related('questions')

    @action(detail=False, methods=['post'])
    def submit(self, request):
        serializer = CreateSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission = AssessmentService.submit_assessment(
            user=request.user,
            **serializer.validated_data,
            **self.get_audit_context()
        )
        return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.filter(
            user=self.request.user
        ).select_related('assessment')
