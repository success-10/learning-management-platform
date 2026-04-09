from django.dispatch import receiver
from apps.core.events import score_calculated, student_enrolled
from .tasks import send_score_notification, send_enrollment_notification


@receiver(score_calculated)
def on_score_calculated(sender, submission_id, user_id, score, passed, **kwargs):
    """Notify student of their assessment result."""
    send_score_notification.delay(submission_id, score, passed)


@receiver(student_enrolled)
def on_student_enrolled(sender, enrollment_id, student_id, course_id, **kwargs):
    """Notify student of successful enrollment."""
    send_enrollment_notification.delay(student_id, course_id)
