from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import AssessmentViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r'assessments', AssessmentViewSet, basename='assessments')
router.register(r'submissions', SubmissionViewSet, basename='submissions')

urlpatterns = [
    path('', include(router.urls)),
]
