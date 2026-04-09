from rest_framework import serializers
from apps.analytics.models import AnalyticsEvent


class AnalyticsEventSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default=None)

    class Meta:
        model = AnalyticsEvent
        fields = ('id', 'username', 'event_type', 'data', 'created_at')
        read_only_fields = fields
