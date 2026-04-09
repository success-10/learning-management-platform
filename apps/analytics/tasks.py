from celery import shared_task
from .models import AnalyticsEvent
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, retry_backoff=True, retry_jitter=True, acks_late=True)
def log_analytics_event(self, user_id, event_type, data):
    """
    Logs an analytics event. Resolves user from user_id if provided.
    Decoupled from other app models — only receives primitive data.
    """
    try:
        user = None
        if user_id:
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning(f"User {user_id} not found for analytics event {event_type}")

        AnalyticsEvent.objects.create(
            user=user,
            event_type=event_type,
            data=data
        )
        return f"Logged {event_type}"

    except Exception as e:
        logger.exception(f"Error logging analytics event: {event_type}")
        self.retry(exc=e, countdown=10)
