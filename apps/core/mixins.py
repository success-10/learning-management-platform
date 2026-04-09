class AuditMixin:
    """
    Mixin for DRF views that provides audit context extraction.
    Avoids repeating IP extraction and path logic in every view.
    """
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR')

    def get_audit_context(self):
        return {
            'path': self.request.path,
            'ip': self.get_client_ip(),
        }
