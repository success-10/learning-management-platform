from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .models import Enrollment
from apps.courses.models import Course
from apps.audit_logs.services import AuditLogService
from apps.core.events import student_enrolled, student_unenrolled


class EnrollmentService:
    @staticmethod
    def _invalidate_enrollment_cache(student_id, course_id):
        cache.delete(f"enrollment_check_{student_id}_{course_id}")

    @staticmethod
    def enroll_student(*, student, course, path=None, ip=None):
        """
        Enrolls a student in a course.
        """
        if not course.is_published:
            raise ValidationError("Cannot enroll in an unpublished course.")

        if Enrollment.objects.filter(student=student, course=course).exists():
            raise ValidationError("Student is already enrolled in this course.")

        with transaction.atomic():
            enrollment = Enrollment.objects.create(
                student=student,
                course=course
            )

            AuditLogService.log(
                user=student,
                action="STUDENT_ENROLLMENT",
                obj=course,
                path=path,
                ip_address=ip
            )

            # Fire domain event and invalidate cache
            transaction.on_commit(
                lambda: [
                    student_enrolled.send(
                        sender=EnrollmentService,
                        enrollment_id=enrollment.id,
                        student_id=student.id,
                        course_id=course.id,
                    ),
                    EnrollmentService._invalidate_enrollment_cache(student.id, course.id)
                ]
            )

        return enrollment

    @staticmethod
    def unenroll_student(*, student, course, path=None, ip=None):
        """
        Removes a student's enrollment from a course.
        """
        try:
            enrollment = Enrollment.objects.get(student=student, course=course)
        except Enrollment.DoesNotExist:
            raise ValidationError("Student is not enrolled in this course.")

        student_id = student.id
        course_id = course.id
        enrollment_id = enrollment.id

        with transaction.atomic():
            AuditLogService.log(
                user=student,
                action="STUDENT_UNENROLLMENT",
                obj=course,
                path=path,
                ip_address=ip
            )
            enrollment.delete()

            # Fire domain event and invalidate cache
            transaction.on_commit(
                lambda: [
                    student_unenrolled.send(
                        sender=EnrollmentService,
                        enrollment_id=enrollment_id,
                        student_id=student_id,
                        course_id=course_id,
                    ),
                    EnrollmentService._invalidate_enrollment_cache(student_id, course_id)
                ]
            )

    @staticmethod
    def get_student_enrollments(student):
        """
        Returns a queryset of enrollments for the student.
        """
        from .selectors import EnrollmentSelector
        return EnrollmentSelector.get_student_enrollments(student)

    @staticmethod
    def is_enrolled(student, course):
        from .selectors import EnrollmentSelector
        return EnrollmentSelector.is_enrolled(student, course)
