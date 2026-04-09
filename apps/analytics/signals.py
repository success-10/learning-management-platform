from django.dispatch import receiver
from apps.core.events import (
    score_calculated, assessment_submitted,
    student_enrolled, course_completed
)
from .tasks import log_analytics_event


@receiver(score_calculated)
def on_score_calculated(sender, submission_id, user_id, course_id, assessment_id, score, passed, **kwargs):
    log_analytics_event.delay(
        user_id=user_id,
        event_type='SCORE_CALCULATED',
        data={
            'submission_id': submission_id,
            'course_id': course_id,
            'assessment_id': assessment_id,
            'score': score,
            'passed': passed,
        }
    )


@receiver(assessment_submitted)
def on_assessment_submitted(sender, submission_id, **kwargs):
    log_analytics_event.delay(
        user_id=None,
        event_type='ASSESSMENT_SUBMITTED',
        data={'submission_id': submission_id}
    )


@receiver(student_enrolled)
def on_student_enrolled(sender, enrollment_id, student_id, course_id, **kwargs):
    log_analytics_event.delay(
        user_id=student_id,
        event_type='STUDENT_ENROLLED',
        data={
            'enrollment_id': enrollment_id,
            'course_id': course_id,
        }
    )


@receiver(course_completed)
def on_course_completed(sender, user_id, course_id, **kwargs):
    log_analytics_event.delay(
        user_id=user_id,
        event_type='COURSE_COMPLETED',
        data={'course_id': course_id}
    )
