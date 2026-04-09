from .models import Course, Module, Lesson
from apps.enrollments.models import Enrollment
from django.db.models import QuerySet, Count
from django.core.cache import cache


class CourseSelector:
    """Read operations for courses."""
    PUBLISHED_COURSES_CACHE_KEY = 'published_courses_list'
    CACHE_TTL = 300  # 5 minutes

    @staticmethod
    def get_published_courses() -> list:
        cached = cache.get(CourseSelector.PUBLISHED_COURSES_CACHE_KEY)
        if cached is not None:
            return cached

        qs = Course.objects.filter(
            is_published=True
        ).select_related('instructor').prefetch_related('modules__lessons')

        courses = list(qs)
        cache.set(CourseSelector.PUBLISHED_COURSES_CACHE_KEY, courses, CourseSelector.CACHE_TTL)
        return courses

    @staticmethod
    def get_instructor_courses(instructor) -> QuerySet:
        return Course.objects.filter(
            instructor=instructor
        ).select_related('instructor').prefetch_related('modules__lessons')

    @staticmethod
    def get_all_courses() -> QuerySet:
        return Course.objects.all().select_related(
            'instructor'
        ).prefetch_related('modules__lessons')

    @staticmethod
    def get_course_by_uuid(uuid):
        return Course.objects.select_related(
            'instructor'
        ).prefetch_related('modules__lessons').get(uuid=uuid)


class ModuleSelector:
    """Read operations for modules."""

    @staticmethod
    def get_instructor_modules(instructor) -> QuerySet:
        return Module.objects.filter(
            course__instructor=instructor
        ).select_related('course').prefetch_related('lessons')

    @staticmethod
    def get_enrolled_student_modules(student) -> QuerySet:
        enrolled_course_ids = Enrollment.objects.filter(
            student=student
        ).values_list('course_id', flat=True)
        return Module.objects.filter(
            course_id__in=enrolled_course_ids
        ).select_related('course').prefetch_related('lessons')

    @staticmethod
    def get_modules_for_course(course_uuid) -> QuerySet:
        return Module.objects.filter(
            course__uuid=course_uuid
        ).prefetch_related('lessons').order_by('order')


class LessonSelector:
    """Read operations for lessons."""

    @staticmethod
    def get_instructor_lessons(instructor) -> QuerySet:
        return Lesson.objects.filter(
            module__course__instructor=instructor
        ).select_related('module__course')

    @staticmethod
    def get_enrolled_student_lessons(student) -> QuerySet:
        enrolled_course_ids = Enrollment.objects.filter(
            student=student
        ).values_list('course_id', flat=True)
        return Lesson.objects.filter(
            module__course_id__in=enrolled_course_ids
        ).select_related('module__course')

    @staticmethod
    def get_lessons_for_module(module_uuid) -> QuerySet:
        return Lesson.objects.filter(
            module__uuid=module_uuid
        ).order_by('order')
