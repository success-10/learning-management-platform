from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.courses.models import Course, Lesson


class UserCourseProgress(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='course_progress', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='student_progress', on_delete=models.CASCADE)
    progress_percent = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} - {self.course} - {self.progress_percent}%"


class LessonCompletion(TimeStampedModel):
    """Tracks individual lesson completions per student."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='lesson_completions',
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        related_name='completions',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'lesson')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} completed {self.lesson.title}"
