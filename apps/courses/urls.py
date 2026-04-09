from django.urls import path, include
from rest_framework_nested import routers
from .api.views import CourseViewSet, ModuleViewSet, LessonViewSet

router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'modules', ModuleViewSet, basename='course-modules')

modules_router = routers.NestedDefaultRouter(courses_router, r'modules', lookup='module')
modules_router.register(r'lessons', LessonViewSet, basename='module-lessons')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(courses_router.urls)),
    path('', include(modules_router.urls)),
]
