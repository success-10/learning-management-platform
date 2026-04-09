from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.core.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health Check
    path('health/', health_check, name='health-check'),

    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Endpoints
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.courses.urls')),
    path('api/v1/', include('apps.enrollments.urls')),
    path('api/v1/assessments/', include('apps.assessments.urls')),
    path('api/v1/progress/', include('apps.progress.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
]
