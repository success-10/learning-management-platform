from .models import AuditLog

class AuditLogService:
    @staticmethod
    def log(*, user, action, obj=None, path=None, ip_address=None):
        """
        Log an action performed by a user.
        
        Args:
            request: The Django request object (to extract user, path, IP).
            action: String description of the action (e.g., "COURSE_PUBLISH").
            obj: Optional model instance receiving the action.
        """
        
        
        object_type = ""
        object_id = ""
        
        if obj:
            object_type = obj.__class__.__name__
            if hasattr(obj, 'uuid'):
                object_id = str(obj.uuid)
            else:
                object_id = str(obj.pk)

        AuditLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            object_type=object_type,
            object_id=object_id,
            path=path,
            ip_address=ip_address
        )

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
