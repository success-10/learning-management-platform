from django.contrib import admin
from .models import Assessment, Question, Submission


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'passing_score', 'created_at')
    list_filter = ('passing_score', 'created_at')
    search_fields = ('title', 'lesson__title')
    readonly_fields = ('uuid', 'created_at', 'updated_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'order', 'points', 'correct_option_index')
    list_filter = ('assessment',)
    search_fields = ('text', 'assessment__title')
    ordering = ('assessment', 'order')
    readonly_fields = ('uuid', 'created_at', 'updated_at')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'status', 'score', 'passed', 'created_at')
    list_filter = ('status', 'passed', 'created_at')
    search_fields = ('user__username', 'assessment__title')
    ordering = ('-created_at',)
    readonly_fields = ('uuid', 'created_at', 'updated_at')
