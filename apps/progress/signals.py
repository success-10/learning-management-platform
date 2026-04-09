from django.dispatch import receiver
from apps.core.events import score_calculated, lesson_completed
from .tasks import update_course_progress_from_score, update_course_progress_from_lesson


@receiver(score_calculated)
def on_score_calculated(sender, submission_id, user_id, course_id, score, passed, **kwargs):
    """
    When a score is calculated, trigger a task to update the user's progress.
    """
    update_course_progress_from_score.delay(user_id, course_id)


@receiver(lesson_completed)
def on_lesson_completed(sender, user_id, lesson_id, course_id, **kwargs):
    """
    When a lesson is completed, trigger a task to update the user's progress.
    """
    update_course_progress_from_lesson.delay(user_id, course_id)
