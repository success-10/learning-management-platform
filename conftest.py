import pytest
from django.core.cache import cache
from apps.accounts.models import User

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

from apps.courses.models import Course, Module, Lesson
from apps.assessments.models import Assessment


@pytest.fixture
def student(db):
    return User.objects.create_user(
        username='student1',
        password='testpass123',
        email='student@test.com',
        role=User.Role.STUDENT
    )


@pytest.fixture
def instructor(db):
    return User.objects.create_user(
        username='instructor1',
        password='testpass123',
        email='instructor@test.com',
        role=User.Role.INSTRUCTOR
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username='admin1',
        password='testpass123',
        email='admin@test.com',
        role=User.Role.ADMIN
    )


@pytest.fixture
def course(db, instructor):
    return Course.objects.create(
        title='Test Course',
        description='A test course description.',
        instructor=instructor,
        is_published=True
    )


@pytest.fixture
def unpublished_course(db, instructor):
    return Course.objects.create(
        title='Draft Course',
        description='An unpublished course.',
        instructor=instructor,
        is_published=False
    )


@pytest.fixture
def module(db, course):
    return Module.objects.create(
        course=course,
        title='Test Module',
        order=1
    )


@pytest.fixture
def lesson(db, module):
    return Lesson.objects.create(
        module=module,
        title='Test Lesson',
        content='Lesson content here',
        content_type=Lesson.ContentType.TEXT,
        order=1,
        duration_minutes=10
    )


@pytest.fixture
def assessment(db, lesson):
    return Assessment.objects.create(
        title='Test Quiz',
        lesson=lesson,
        passing_score=70
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_student_client(api_client, student):
    api_client.force_authenticate(user=student)
    return api_client


@pytest.fixture
def authenticated_instructor_client(api_client, instructor):
    api_client.force_authenticate(user=instructor)
    return api_client
