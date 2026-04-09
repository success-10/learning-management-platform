from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        INSTRUCTOR = 'INSTRUCTOR', 'Instructor'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )
    
    # Optional: Add extra profile fields here or link to a Profile model
    bio = models.TextField(blank=True)

    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR
    
    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_admin_role(self):
        return self.role == self.Role.ADMIN
