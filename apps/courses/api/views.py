from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.courses.models import Course, Module, Lesson
from apps.courses.api.serializers import (
    CourseSerializer, CreateCourseSerializer,
    ModuleSerializer, CreateModuleSerializer,
    LessonSerializer, CreateLessonSerializer
)
from apps.courses.api.filters import CourseFilter
from apps.courses.services import CourseService, ModuleService, LessonService
from apps.courses.selectors import CourseSelector, ModuleSelector, LessonSelector
from apps.enrollments.services import EnrollmentService
from apps.accounts.permissions import IsInstructor, IsStudent
from apps.accounts.models import User
from apps.core.mixins import AuditMixin


class CourseViewSet(AuditMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateCourseSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy', 'publish']:
            return [permissions.IsAuthenticated(), IsInstructor()]
        elif self.action == 'enroll':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or user.role == User.Role.STUDENT:
            return CourseSelector.get_published_courses()

        if user.role == User.Role.INSTRUCTOR:
            return CourseSelector.get_instructor_courses(user)

        if user.role == User.Role.ADMIN:
            return CourseSelector.get_all_courses()

        return Course.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = CourseService.create_course(
            **serializer.validated_data,
            instructor=request.user,
            **self.get_audit_context()
        )
        return Response(CourseSerializer(course).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)

        CourseService.update_course(
            course=course,
            instructor=request.user,
            **self.get_audit_context(),
            **serializer.validated_data
        )
        return Response(CourseSerializer(course).data)

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        CourseService.delete_course(
            course=course,
            instructor=request.user,
            **self.get_audit_context()
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def publish(self, request, uuid=None):
        course = self.get_object()
        try:
            CourseService.publish_course(
                course=course,
                instructor=request.user,
                **self.get_audit_context()
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Course published"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, uuid=None):
        course = self.get_object()
        try:
            CourseService.unpublish_course(
                course=course,
                instructor=request.user,
                **self.get_audit_context()
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Course unpublished"})

    @action(detail=True, methods=['post'])
    def enroll(self, request, uuid=None):
        # use the model directly to find the course even if unpublished, 
        # so the Service can return a 400 "Course is not published" instead of a 404.
        try:
            course = Course.objects.get(uuid=uuid)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            EnrollmentService.enroll_student(
                student=request.user,
                course=course,
                **self.get_audit_context()
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Enrolled successfully"}, status=status.HTTP_201_CREATED)


class ModuleViewSet(AuditMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateModuleSerializer
        return ModuleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.INSTRUCTOR:
            return ModuleSelector.get_instructor_modules(user)

        if user.role == User.Role.STUDENT:
            return ModuleSelector.get_enrolled_student_modules(user)

        return Module.objects.none()

    def perform_create(self, serializer):
        course_uuid = self.kwargs.get('course_pk')
        course = CourseSelector.get_course_by_uuid(course_uuid)

        ModuleService.create_module(
            course=course,
            instructor=self.request.user,
            **self.get_audit_context(),
            **serializer.validated_data
        )

    def perform_update(self, serializer):
        module = self.get_object()
        ModuleService.update_module(
            module=module,
            instructor=self.request.user,
            **self.get_audit_context(),
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        ModuleService.delete_module(
            module=instance,
            instructor=self.request.user,
            **self.get_audit_context()
        )


class LessonViewSet(AuditMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateLessonSerializer
        return LessonSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.INSTRUCTOR:
            return LessonSelector.get_instructor_lessons(user)

        if user.role == User.Role.STUDENT:
            return LessonSelector.get_enrolled_student_lessons(user)

        return Lesson.objects.none()

    def perform_create(self, serializer):
        module_uuid = self.kwargs.get('module_pk')
        module = Module.objects.get(uuid=module_uuid)

        LessonService.create_lesson(
            module=module,
            instructor=self.request.user,
            **self.get_audit_context(),
            **serializer.validated_data
        )

    def perform_update(self, serializer):
        lesson = self.get_object()
        LessonService.update_lesson(
            lesson=lesson,
            instructor=self.request.user,
            **self.get_audit_context(),
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        LessonService.delete_lesson(
            lesson=instance,
            instructor=self.request.user,
            **self.get_audit_context()
        )