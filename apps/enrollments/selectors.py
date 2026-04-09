from apps.enrollments.models import Enrollment
from django.db.models import QuerySet
from django.core.cache import cache


class EnrollmentSelector:
    """Read operations for enrollments."""

    @staticmethod
    def get_student_enrollments(student) -> QuerySet:
        return Enrollment.objects.filter(
            student=student
        ).select_related('course', 'course__instructor')

    @staticmethod
    def get_course_enrollments(course) -> QuerySet:
        return Enrollment.objects.filter(
            course=course
        ).select_related('student')

    @staticmethod
    def is_enrolled(student, course) -> bool:
        cache_key = f"enrollment_check_{student.id}_{course.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        exists = Enrollment.objects.filter(
            student=student, course=course
        ).exists()
        cache.set(cache_key, exists, 3600)
        return exists

    @staticmethod
    def get_enrolled_student_count(course) -> int:
        return Enrollment.objects.filter(course=course).count()
