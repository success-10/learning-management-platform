from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import EnrollmentViewSet

router = DefaultRouter()
router.register(r'my-enrollments', EnrollmentViewSet, basename='my-enrollments')

urlpatterns = [
    path('', include(router.urls)),
]
