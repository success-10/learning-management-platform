from rest_framework import serializers
from apps.enrollments.models import Enrollment
from apps.courses.api.serializers import CourseSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ('uuid', 'course', 'created_at')
