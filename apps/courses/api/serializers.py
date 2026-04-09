from rest_framework import serializers
from apps.courses.models import Course, Module, Lesson
from apps.accounts.api.serializers import UserSerializer

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('uuid', 'title', 'content', 'content_type', 'order', 'duration_minutes', 'created_at')
        read_only_fields = ('uuid', 'created_at')

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    class Meta:
        model = Module
        fields = ('uuid', 'title', 'order', 'lessons', 'created_at')
        read_only_fields = ('uuid', 'created_at', 'lessons')

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ('uuid', 'title', 'description', 'instructor', 'is_published', 'modules', 'created_at')
        read_only_fields = ('uuid', 'instructor', 'modules', 'created_at')

class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'description', 'is_published')

class CreateModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ('title', 'order')

class CreateLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('title', 'content', 'content_type', 'order', 'duration_minutes')
