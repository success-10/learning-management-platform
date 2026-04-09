from apps.accounts.models import User
from apps.audit_logs.services import AuditLogService


class AccountService:
    @staticmethod
    def register_user(*, username, password, email, first_name='',
                      last_name='', path=None, ip=None):
        """
        Registers a new user with the STUDENT role by default.
        """
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        AuditLogService.log(
            user=user,
            action="USER_REGISTER",
            obj=user,
            path=path,
            ip_address=ip
        )
        return user
