import pytest
from django.core.exceptions import ValidationError
from django.core.cache import cache
from apps.enrollments.services import EnrollmentService
from apps.enrollments.models import Enrollment


@pytest.mark.django_db
class TestEnrollmentService:
    """Tests for EnrollmentService business logic."""

    def test_enroll_student(self, student, course):
        enrollment = EnrollmentService.enroll_student(
            student=student,
            course=course
        )
        assert enrollment.student == student
        assert enrollment.course == course

    def test_enroll_unpublished_course(self, student, unpublished_course):
        with pytest.raises(ValidationError, match="unpublished"):
            EnrollmentService.enroll_student(
                student=student,
                course=unpublished_course
            )

    def test_duplicate_enrollment(self, student, course):
        EnrollmentService.enroll_student(student=student, course=course)
        with pytest.raises(ValidationError, match="already enrolled"):
            EnrollmentService.enroll_student(student=student, course=course)

    def test_get_student_enrollments(self, student, course):
        EnrollmentService.enroll_student(student=student, course=course)
        enrollments = EnrollmentService.get_student_enrollments(student)
        assert enrollments.count() == 1

    def test_is_enrolled(self, student, course):
        assert EnrollmentService.is_enrolled(student, course) is False
        EnrollmentService.enroll_student(student=student, course=course)
        cache.clear() # Cache invalidation usually happens on_commit, which doesn't fire in tests
        assert EnrollmentService.is_enrolled(student, course) is True
