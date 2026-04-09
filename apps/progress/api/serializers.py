from rest_framework import serializers
from apps.progress.models import UserCourseProgress, LessonCompletion


class UserCourseProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_uuid = serializers.UUIDField(source='course.uuid', read_only=True)

    class Meta:
        model = UserCourseProgress
        fields = (
            'id', 'course_uuid', 'course_title',
            'progress_percent', 'is_completed', 'completed_at', 'updated_at'
        )
        read_only_fields = fields


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_uuid = serializers.UUIDField(source='lesson.uuid', read_only=True)

    class Meta:
        model = LessonCompletion
        fields = ('id', 'lesson_uuid', 'lesson_title', 'created_at')
        read_only_fields = fields


class MarkLessonCompleteSerializer(serializers.Serializer):
    lesson_uuid = serializers.UUIDField()
