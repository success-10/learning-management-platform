from django.dispatch import receiver
from apps.core.events import assessment_submitted


@receiver(assessment_submitted)
def on_assessment_submitted(sender, submission_id, **kwargs):
    """
    Listener for assessment_submitted.
    Triggers the scoring background task.
    """
    from .tasks import calculate_score
    calculate_score.delay(submission_id)

# Note: score_calculated listeners will be in other apps (progress, analytics)
