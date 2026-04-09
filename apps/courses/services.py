from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .models import Course, Module, Lesson
from .selectors import CourseSelector
from apps.audit_logs.services import AuditLogService
from apps.core.events import course_created, course_published, course_unpublished


class CourseService:
    @staticmethod
    def _invalidate_course_cache():
        cache.delete(CourseSelector.PUBLISHED_COURSES_CACHE_KEY)

    @staticmethod
    def create_course(*, title, description, instructor, path=None, ip=None):
        course = Course.objects.create(
            title=title,
            description=description,
            instructor=instructor
        )

        AuditLogService.log(
            user=instructor,
            action="COURSE_CREATE",
            obj=course,
            path=path,
            ip_address=ip
        )

        # Fire domain event and invalidate cache after commit
        transaction.on_commit(
            lambda: [
                course_created.send(
                    sender=CourseService,
                    course_id=course.id,
                    instructor_id=instructor.id,
                ),
                CourseService._invalidate_course_cache()
            ]
        )
        return course

    @staticmethod
    def update_course(course, instructor, *, path=None, ip=None, **data):
        if course.instructor != instructor:
            raise ValidationError("You cannot update another instructor's course.")

        for key, value in data.items():
            setattr(course, key, value)

        course.save()

        AuditLogService.log(
            user=instructor,
            action="COURSE_UPDATE",
            obj=course,
            path=path,
            ip_address=ip
        )
        transaction.on_commit(CourseService._invalidate_course_cache)
        return course

    @staticmethod
    def delete_course(course, instructor, *, path=None, ip=None):
        if course.instructor != instructor:
            raise ValidationError("You cannot delete another instructor's course.")

        if course.is_published:
            raise ValidationError("Unpublish the course before deleting.")

        AuditLogService.log(
            user=instructor,
            action="COURSE_DELETE",
            obj=course,
            path=path,
            ip_address=ip
        )
        course.delete()
        transaction.on_commit(CourseService._invalidate_course_cache)

    @staticmethod
    def publish_course(course, instructor, *, path=None, ip=None):
        if course.instructor != instructor:
            raise ValidationError("You cannot publish another instructor's course.")

        if course.is_published:
            raise ValidationError("Course is already published.")

        course.is_published = True
        course.save(update_fields=["is_published"])

        AuditLogService.log(
            user=instructor,
            action="COURSE_PUBLISH",
            obj=course,
            path=path,
            ip_address=ip
        )

        # Fire domain event and invalidate cache after commit
        transaction.on_commit(
            lambda: [
                course_published.send(
                    sender=CourseService,
                    course_id=course.id,
                    instructor_id=instructor.id,
                ),
                CourseService._invalidate_course_cache()
            ]
        )
        return course

    @staticmethod
    def unpublish_course(course, instructor, *, path=None, ip=None):
        if course.instructor != instructor:
            raise ValidationError("You cannot unpublish another instructor's course.")

        course.is_published = False
        course.save(update_fields=["is_published"])

        AuditLogService.log(
            user=instructor,
            action="COURSE_UNPUBLISH",
            obj=course,
            path=path,
            ip_address=ip
        )

        # Fire domain event and invalidate cache after commit
        transaction.on_commit(
            lambda: [
                course_unpublished.send(
                    sender=CourseService,
                    course_id=course.id,
                    instructor_id=instructor.id,
                ),
                CourseService._invalidate_course_cache()
            ]
        )
        return course


class ModuleService:
    @staticmethod
    def create_module(*, course, title, instructor, order=0, path=None, ip=None):
        if course.instructor != instructor:
            raise ValidationError("You can only add modules to your own courses.")

        module = Module.objects.create(
            course=course,
            title=title,
            order=order
        )
        AuditLogService.log(
            user=instructor,
            action="MODULE_CREATE",
            obj=module,
            path=path,
            ip_address=ip
        )
        transaction.on_commit(CourseService._invalidate_course_cache)
        return module

    @staticmethod
    def update_module(module, instructor, *, path=None, ip=None, **kwargs):
        if module.course.instructor != instructor:
            raise ValidationError("You can only update modules in your own courses.")

        for key, value in kwargs.items():
            setattr(module, key, value)
        module.save()

        AuditLogService.log(
            user=instructor,
            action="MODULE_UPDATE",
            obj=module,
            path=path,
            ip_address=ip
        )
        transaction.on_commit(CourseService._invalidate_course_cache)
        return module

    @staticmethod
    def delete_module(module, instructor, *, path=None, ip=None):
        if module.course.instructor != instructor:
            raise ValidationError("You can only delete modules in your own courses.")

        AuditLogService.log(
            user=instructor,
            action="MODULE_DELETE",
            obj=module,
            path=path,
            ip_address=ip
        )
        module.delete()
        transaction.on_commit(CourseService._invalidate_course_cache)


class LessonService:
    @staticmethod
    def create_lesson(*, module, title, content, content_type, instructor, order=0, duration_minutes=0, path=None, ip=None):
        if module.course.instructor != instructor:
            raise ValidationError("You can only add lessons to your own courses.")

        lesson = Lesson.objects.create(
            module=module,
            title=title,
            content=content,
            content_type=content_type,
            order=order,
            duration_minutes=duration_minutes
        )

        AuditLogService.log(
            user=instructor,
            action="LESSON_CREATE",
            obj=lesson,
            path=path,
            ip_address=ip
        )
        transaction.on_commit(CourseService._invalidate_course_cache)
        return lesson

    @staticmethod
    def update_lesson(lesson, instructor, *, path=None, ip=None, **kwargs):
        if lesson.module.course.instructor != instructor:
            raise ValidationError("You can only update lessons in your own courses.")

        for key, value in kwargs.items():
            setattr(lesson, key, value)
        lesson.save()

        AuditLogService.log(
            user=instructor,
            action="LESSON_UPDATE",
            obj=lesson,
            path=path,
            ip_address=ip
        )
        transaction.on_commit(CourseService._invalidate_course_cache)
        return lesson

    @staticmethod
    def delete_lesson(lesson, instructor, *, path=None, ip=None):
        if lesson.module.course.instructor != instructor:
            raise ValidationError("You can only delete lessons in your own courses.")

        AuditLogService.log(
            user=instructor,
            action="LESSON_DELETE",
            obj=lesson,
            path=path,
            ip_address=ip
        )
        lesson.delete()
        transaction.on_commit(CourseService._invalidate_course_cache)
