import pytest
from rest_framework import status
from apps.courses.models import Course
from apps.accounts.models import User


@pytest.mark.django_db
class TestCourseAPI:
    """Tests for Course API permissions and responses."""

    def test_list_courses_unauthenticated(self, api_client, course):
        response = api_client.get('/api/v1/courses/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_course_as_student_forbidden(self, authenticated_student_client):
        response = authenticated_student_client.post('/api/v1/courses/', {
            'title': 'Student Course',
            'description': 'Should fail'
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_course_as_instructor(self, authenticated_instructor_client):
        response = authenticated_instructor_client.post('/api/v1/courses/', {
            'title': 'Instructor Course',
            'description': 'Should succeed'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Instructor Course'

    def test_instructor_sees_own_courses(self, authenticated_instructor_client, course, instructor):
        # Create another instructor with a course
        other = User.objects.create_user(
            username='other_instructor', password='pass123',
            role=User.Role.INSTRUCTOR
        )
        Course.objects.create(
            title='Other Course', description='Not mine',
            instructor=other, is_published=True
        )

        response = authenticated_instructor_client.get('/api/v1/courses/')
        assert response.status_code == status.HTTP_200_OK
        titles = [c['title'] for c in response.data['results']]
        assert 'Test Course' in titles
        assert 'Other Course' not in titles

    def test_student_sees_only_published(self, authenticated_student_client, course, unpublished_course):
        response = authenticated_student_client.get('/api/v1/courses/')
        assert response.status_code == status.HTTP_200_OK
        titles = [c['title'] for c in response.data['results']]
        assert 'Test Course' in titles
        assert 'Draft Course' not in titles


@pytest.mark.django_db
class TestEnrollmentAPI:
    """Tests for enrollment via CourseViewSet."""

    def test_enroll_in_published_course(self, authenticated_student_client, course):
        response = authenticated_student_client.post(
            f'/api/v1/courses/{course.uuid}/enroll/'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_enroll_in_unpublished_course(self, authenticated_student_client, unpublished_course):
        response = authenticated_student_client.post(
            f'/api/v1/courses/{unpublished_course.uuid}/enroll/'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_double_enrollment_rejected(self, authenticated_student_client, course):
        authenticated_student_client.post(f'/api/v1/courses/{course.uuid}/enroll/')
        response = authenticated_student_client.post(
            f'/api/v1/courses/{course.uuid}/enroll/'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
