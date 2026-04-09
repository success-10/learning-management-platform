from django.db import transaction
from django.core.exceptions import ValidationError
from .models import LessonCompletion, UserCourseProgress
from apps.courses.models import Lesson
from apps.enrollments.services import EnrollmentService
from apps.audit_logs.services import AuditLogService
from apps.core.events import lesson_completed
import logging

logger = logging.getLogger(__name__)


class ProgressService:
    @staticmethod
    def mark_lesson_completed(*, user, lesson_uuid, path=None, ip=None):
        """
        Marks a lesson as completed for a student.
        Fires lesson_completed event on success.

        Raises:
            ValidationError: If lesson not found, not enrolled, or already completed.
        """
        try:
            lesson = Lesson.objects.select_related('module__course').get(uuid=lesson_uuid)
        except Lesson.DoesNotExist:
            raise ValidationError("Lesson not found.")

        course = lesson.module.course

        # Verify enrollment
        if not EnrollmentService.is_enrolled(user, course):
            raise ValidationError("You must be enrolled in this course to complete lessons.")

        # Check idempotency
        if LessonCompletion.objects.filter(user=user, lesson=lesson).exists():
            raise ValidationError("Lesson already completed.")

        with transaction.atomic():
            completion = LessonCompletion.objects.create(user=user, lesson=lesson)

            AuditLogService.log(
                user=user,
                action="LESSON_COMPLETED",
                obj=lesson,
                path=path,
                ip_address=ip
            )

            # Fire event after commit
            transaction.on_commit(
                lambda: lesson_completed.send(
                    sender=ProgressService,
                    user_id=user.id,
                    lesson_id=lesson.id,
                    course_id=course.id,
                )
            )

        return completion

    @staticmethod
    def get_course_progress(user, course):
        """
        Calculate the overall progress for a user in a course.
        Progress is based on:
          - Lessons completed / total lessons (50% weight)
          - Assessments passed / total assessments (50% weight)
        """
        from apps.assessments.models import Assessment, Submission

        total_lessons = Lesson.objects.filter(module__course=course).count()
        completed_lessons = LessonCompletion.objects.filter(
            user=user, lesson__module__course=course
        ).count()

        total_assessments = Assessment.objects.filter(
            lesson__module__course=course
        ).count()
        passed_assessments = Submission.objects.filter(
            user=user,
            assessment__lesson__module__course=course,
            passed=True
        ).values('assessment').distinct().count()

        # Calculate weighted progress
        lesson_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        assessment_progress = (passed_assessments / total_assessments * 100) if total_assessments > 0 else 0

        if total_lessons > 0 and total_assessments > 0:
            # Both exist — 50/50 weight
            overall = (lesson_progress + assessment_progress) / 2
        elif total_lessons > 0:
            overall = lesson_progress
        elif total_assessments > 0:
            overall = assessment_progress
        else:
            overall = 0

        return {
            'overall_percent': round(overall, 1),
            'lessons_completed': completed_lessons,
            'total_lessons': total_lessons,
            'assessments_passed': passed_assessments,
            'total_assessments': total_assessments,
        }
