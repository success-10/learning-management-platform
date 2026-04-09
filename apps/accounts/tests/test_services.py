import pytest
from apps.accounts.services import AccountService
from apps.accounts.models import User

@pytest.mark.django_db
class TestAccountService:
    def test_register_user(self):
        user = AccountService.register_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        assert User.objects.count() == 1
        assert user.username == 'testuser'
        assert user.role == User.Role.STUDENT
        assert user.is_active is True

    def test_user_roles(self):
        student = User.objects.create_user(username='s', role=User.Role.STUDENT)
        instructor = User.objects.create_user(username='i', role=User.Role.INSTRUCTOR)
        admin = User.objects.create_user(username='a', role=User.Role.ADMIN)

        assert student.role == 'STUDENT'
        assert instructor.role == 'INSTRUCTOR'
        assert admin.role == 'ADMIN'
