import pytest
from apps.audit_logs.services import AuditLogService
from apps.audit_logs.models import AuditLog

@pytest.mark.django_db
class TestAuditLogService:
    def test_log_action(self, student, course):
        AuditLogService.log(
            user=student,
            action='TEST_ACTION',
            obj=course,
            path='/test/',
            ip_address='127.0.0.1'
        )
        log = AuditLog.objects.first()
        assert log.user == student
        assert log.action == 'TEST_ACTION'
        assert log.object_type == 'Course'
        assert log.object_id == str(course.uuid)
        assert log.path == '/test/'
        assert log.ip_address == '127.0.0.1'
