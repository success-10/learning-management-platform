from rest_framework import permissions
from apps.accounts.models import User


class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_instructor()


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin_role()


class IsOwnerInstructor(permissions.BasePermission):
    """
    Object-level permission that checks the authenticated instructor
    owns the resource being accessed.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Direct course ownership
        if hasattr(obj, 'instructor'):
            return obj.instructor == request.user

        # Module -> Course ownership
        if hasattr(obj, 'course') and hasattr(obj.course, 'instructor'):
            return obj.course.instructor == request.user

        # Lesson -> Module -> Course ownership
        if hasattr(obj, 'module') and hasattr(obj.module, 'course'):
            return obj.module.course.instructor == request.user

        return False
