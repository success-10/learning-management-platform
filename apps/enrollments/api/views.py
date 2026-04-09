from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import EnrollmentSerializer
from apps.enrollments.services import EnrollmentService
from apps.enrollments.selectors import EnrollmentSelector
from apps.core.mixins import AuditMixin


class EnrollmentViewSet(AuditMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing and managing enrollments.
    Enrollment creation is handled via CourseViewSet.enroll action.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EnrollmentSelector.get_student_enrollments(self.request.user)

    @action(detail=True, methods=['delete'])
    def unenroll(self, request, pk=None):
        """Unenroll from a course."""
        enrollment = self.get_object()
        EnrollmentService.unenroll_student(
            student=request.user,
            course=enrollment.course,
            **self.get_audit_context()
        )
        return Response(
            {"message": "Successfully unenrolled."},
            status=status.HTTP_200_OK
        )
