from django.db import models
from django.conf import settings
import uuid
from apps.core.models import TimeStampedModel

class Course(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Module(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    class ContentType(models.TextChoices):
        VIDEO = 'VIDEO', 'Video'
        TEXT = 'TEXT', 'Text'
        DOCUMENT = 'DOCUMENT', 'Document'

    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Markdown content or Video URL")
    content_type = models.CharField(max_length=10, choices=ContentType.choices, default=ContentType.TEXT)
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Estimated duration")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


