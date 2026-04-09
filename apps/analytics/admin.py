from django.contrib import admin
from .models import AnalyticsEvent


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('user__username', 'event_type')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
