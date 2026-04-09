import pytest
from apps.analytics.models import AnalyticsEvent

@pytest.mark.django_db
class TestAnalyticsModel:
    def test_create_event(self, student):
        event = AnalyticsEvent.objects.create(
            user=student,
            event_type='LOGIN',
            data={'source': 'web'}
        )
        assert AnalyticsEvent.objects.count() == 1
        assert event.event_type == 'LOGIN'
        assert event.data['source'] == 'web'
