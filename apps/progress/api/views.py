from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.progress.models import UserCourseProgress, LessonCompletion
from apps.progress.services import ProgressService
from .serializers import (
    UserCourseProgressSerializer, LessonCompletionSerializer, MarkLessonCompleteSerializer
)
from apps.audit_logs.services import AuditLogService


class UserCourseProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user's course progress and completing lessons.
    """
    serializer_class = UserCourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCourseProgress.objects.filter(
            user=self.request.user
        ).select_related('course', 'course__instructor')

    @action(detail=False, methods=['get'])
    def lesson_completions(self, request):
        """List all lessons the user has completed."""
        completions = LessonCompletion.objects.filter(
            user=request.user
        ).select_related('lesson').order_by('-created_at')

        page = self.paginate_queryset(completions)
        if page is not None:
            serializer = LessonCompletionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = LessonCompletionSerializer(completions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def complete_lesson(self, request):
        """Mark a lesson as completed."""
        serializer = MarkLessonCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            completion = ProgressService.mark_lesson_completed(
                user=request.user,
                lesson_uuid=serializer.validated_data['lesson_uuid'],
                path=request.path,
                ip=AuditLogService._get_client_ip(request)
            )
            return Response(
                LessonCompletionSerializer(completion).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
