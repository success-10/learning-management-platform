from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class AnalyticsEvent(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=100)
    data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.event_type} - {self.user}"
