import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.courses.models import Lesson

class Assessment(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=255)
    lesson = models.ForeignKey(Lesson, related_name='assessments', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70)

    def __str__(self):
        return self.title

class Question(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    options = models.JSONField(help_text="List of options, e.g. ['A', 'B', 'C']")
    correct_option_index = models.PositiveIntegerField(help_text="Index of correct option in options list")
    points = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['order']

    def clean(self):
        if self.correct_option_index >= len(self.options):
            raise ValidationError("Correct option index out of range.")

    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}"

class Submission(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SCORED = 'SCORED', 'Scored'
        FAILED = 'FAILED', 'Failed Processing'

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submissions', on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, related_name='submissions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    # Store answers relative to question IDs
    answers = models.JSONField(help_text="Dict of {question_id: selected_index}")

    class Meta:
        unique_together = ('user', 'assessment')

    def __str__(self):
        return f"{self.user.username} - {self.assessment.title}"
