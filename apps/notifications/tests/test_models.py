import pytest
from apps.notifications.models import Notification

@pytest.mark.django_db
class TestNotificationModel:
    def test_create_notification(self, student):
        notification = Notification.objects.create(
            user=student,
            title='Test Title',
            message='Test Message'
        )
        assert Notification.objects.count() == 1
        assert notification.user == student
        assert notification.is_read is False

    def test_mark_as_read(self, student):
        notification = Notification.objects.create(
            user=student,
            title='Test',
            message='Test'
        )
        notification.is_read = True
        notification.save()
        assert Notification.objects.get(id=notification.id).is_read is True
