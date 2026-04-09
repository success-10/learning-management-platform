import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class Enrollment(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    # We reference Course by string to avoid circular imports if Course is modifying,
    # but practically we need to import it or usage 'courses.Course'.
    # 'apps.courses.Course' is safer if lazy loading is needed.
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} -> {self.course}"
