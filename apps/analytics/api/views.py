from rest_framework import viewsets, permissions
from rest_framework.pagination import CursorPagination
from apps.analytics.models import AnalyticsEvent
from .serializers import AnalyticsEventSerializer
from apps.accounts.permissions import IsAdmin


class AnalyticsEventCursorPagination(CursorPagination):
    """Cursor-based pagination for time-ordered, append-only analytics data."""
    page_size = 50
    ordering = '-created_at'
    cursor_query_param = 'cursor'


class AnalyticsEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only endpoint for viewing analytics events.
    Uses cursor-based pagination for scalability with large datasets.
    """
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    pagination_class = AnalyticsEventCursorPagination

    def get_queryset(self):
        qs = AnalyticsEvent.objects.select_related('user').all()

        # Optional filters via query params
        event_type = self.request.query_params.get('event_type')
        if event_type:
            qs = qs.filter(event_type=event_type)

        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)

        return qs
