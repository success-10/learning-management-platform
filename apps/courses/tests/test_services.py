import pytest
from django.core.exceptions import ValidationError
from apps.courses.services import CourseService, ModuleService, LessonService
from apps.courses.models import Course, Module, Lesson
from apps.accounts.models import User


@pytest.mark.django_db
class TestCourseService:
    """Tests for CourseService business logic."""

    def test_create_course(self, instructor):
        course = CourseService.create_course(
            title='New Course',
            description='A great course',
            instructor=instructor
        )
        assert course.title == 'New Course'
        assert course.instructor == instructor
        assert course.is_published is False

    def test_update_course(self, instructor, course):
        updated = CourseService.update_course(
            course=course,
            instructor=instructor,
            title='Updated Title'
        )
        assert updated.title == 'Updated Title'

    def test_update_course_wrong_instructor(self, student, course):
        with pytest.raises(ValidationError, match="cannot update"):
            CourseService.update_course(
                course=course,
                instructor=student,
                title='Hacked'
            )

    def test_publish_course(self, instructor, unpublished_course):
        result = CourseService.publish_course(
            course=unpublished_course,
            instructor=instructor
        )
        assert result.is_published is True

    def test_publish_already_published(self, instructor, course):
        with pytest.raises(ValidationError, match="already published"):
            CourseService.publish_course(
                course=course,
                instructor=instructor
            )

    def test_unpublish_course(self, instructor, course):
        result = CourseService.unpublish_course(
            course=course,
            instructor=instructor
        )
        assert result.is_published is False

    def test_delete_course_must_be_unpublished(self, instructor, course):
        with pytest.raises(ValidationError, match="Unpublish"):
            CourseService.delete_course(
                course=course,
                instructor=instructor
            )

    def test_delete_unpublished_course(self, instructor, unpublished_course):
        course_id = unpublished_course.id
        CourseService.delete_course(
            course=unpublished_course,
            instructor=instructor
        )
        assert not Course.objects.filter(id=course_id).exists()

    def test_delete_course_wrong_instructor(self, student, unpublished_course):
        with pytest.raises(ValidationError, match="cannot delete"):
            CourseService.delete_course(
                course=unpublished_course,
                instructor=student
            )


@pytest.mark.django_db
class TestModuleService:
    """Tests for ModuleService business logic."""

    def test_create_module(self, instructor, course):
        module = ModuleService.create_module(
            course=course,
            title='Module 1',
            instructor=instructor,
            order=1
        )
        assert module.course == course
        assert module.title == 'Module 1'
        assert module.order == 1

    def test_create_module_wrong_instructor(self, student, course):
        with pytest.raises(ValidationError, match="own courses"):
            ModuleService.create_module(
                course=course,
                title='Stolen Module',
                instructor=student
            )

    def test_delete_module(self, instructor, module):
        module_id = module.id
        ModuleService.delete_module(module=module, instructor=instructor)
        assert not Module.objects.filter(id=module_id).exists()


@pytest.mark.django_db
class TestLessonService:
    """Tests for LessonService business logic."""

    def test_create_lesson(self, instructor, module):
        lesson = LessonService.create_lesson(
            module=module,
            title='Lesson 1',
            content='Some content',
            content_type='TEXT',
            instructor=instructor,
            order=1,
            duration=15
        )
        assert lesson.module == module
        assert lesson.title == 'Lesson 1'
        assert lesson.duration_minutes == 15

    def test_create_lesson_wrong_instructor(self, student, module):
        with pytest.raises(ValidationError, match="own courses"):
            LessonService.create_lesson(
                module=module,
                title='Stolen Lesson',
                content='Hacked',
                content_type='TEXT',
                instructor=student
            )
