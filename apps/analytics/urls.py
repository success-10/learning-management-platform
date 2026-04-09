from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import AnalyticsEventViewSet

router = DefaultRouter()
router.register(r'events', AnalyticsEventViewSet, basename='analytics-events')

urlpatterns = [
    path('', include(router.urls)),
]
