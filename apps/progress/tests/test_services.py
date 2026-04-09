import pytest
from django.core.exceptions import ValidationError
from apps.progress.services import ProgressService
from apps.progress.models import LessonCompletion
from apps.enrollments.services import EnrollmentService

@pytest.mark.django_db
class TestProgressService:
    def test_mark_lesson_completed(self, student, course, lesson):
        # Must be enrolled to complete lessons
        EnrollmentService.enroll_student(student=student, course=course)
        
        completion = ProgressService.mark_lesson_completed(
            user=student,
            lesson_uuid=lesson.uuid
        )
        assert LessonCompletion.objects.count() == 1
        assert completion.user == student
        assert completion.lesson == lesson

    def test_mark_lesson_not_enrolled_fails(self, student, lesson):
        with pytest.raises(ValidationError, match="must be enrolled"):
            ProgressService.mark_lesson_completed(
                user=student,
                lesson_uuid=lesson.uuid
            )

    def test_mark_lesson_already_completed_fails(self, student, course, lesson):
        EnrollmentService.enroll_student(student=student, course=course)
        ProgressService.mark_lesson_completed(user=student, lesson_uuid=lesson.uuid)
        
        with pytest.raises(ValidationError, match="already completed"):
            ProgressService.mark_lesson_completed(user=student, lesson_uuid=lesson.uuid)

    def test_get_course_progress(self, student, course, lesson):
        EnrollmentService.enroll_student(student=student, course=course)
        
        # Initially 0
        p = ProgressService.get_course_progress(student, course)
        assert p['overall_percent'] == 0.0
        
        # Complete the only lesson
        ProgressService.mark_lesson_completed(user=student, lesson_uuid=lesson.uuid)
        
        p = ProgressService.get_course_progress(student, course)
        assert p['overall_percent'] == 100.0
        assert p['lessons_completed'] == 1
