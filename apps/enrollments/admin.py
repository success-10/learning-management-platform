from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    list_filter = ('created_at', 'course')
    search_fields = ('student__username', 'course__title')
    ordering = ('-created_at',)
    readonly_fields = ('uuid', 'created_at', 'updated_at')
