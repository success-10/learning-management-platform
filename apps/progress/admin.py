from django.contrib import admin
from .models import UserCourseProgress


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percent', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'course__title')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
