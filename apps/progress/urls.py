from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import UserCourseProgressViewSet

router = DefaultRouter()
router.register(r'', UserCourseProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
]
