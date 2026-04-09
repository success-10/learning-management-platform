from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'object_type', 'object_id', 'ip_address', 'created_at')
    list_filter = ('action', 'object_type', 'created_at')
    search_fields = ('user__username', 'object_id', 'action')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 'path')
    date_hierarchy = 'created_at'
