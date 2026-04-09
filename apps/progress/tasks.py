from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import UserCourseProgress
from apps.courses.models import Course
from apps.core.events import course_completed
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, retry_backoff=True, retry_jitter=True, acks_late=True)
def update_course_progress_from_score(self, user_id, course_id):
    """Recalculate course progress after an assessment is scored."""
    _recalculate_progress(self, user_id, course_id)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, retry_backoff=True, retry_jitter=True, acks_late=True)
def update_course_progress_from_lesson(self, user_id, course_id):
    """Recalculate course progress after a lesson is completed."""
    _recalculate_progress(self, user_id, course_id)


def _recalculate_progress(task_self, user_id, course_id):
    """
    Shared logic to recalculate course progress from both
    lesson completions and assessment results.
    """
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)

        # Use the ProgressService for calculation
        from .services import ProgressService
        stats = ProgressService.get_course_progress(user, course)

        percent = stats['overall_percent']

        progress, created = UserCourseProgress.objects.get_or_create(
            user=user, course=course
        )
        progress.progress_percent = percent

        if percent >= 100 and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            logger.info(f"User {user.username} completed course {course.title}")

            # Fire course_completed event
            from django.db import transaction
            transaction.on_commit(
                lambda: course_completed.send(
                    sender=UserCourseProgress,
                    user_id=user_id,
                    course_id=course_id,
                )
            )

        progress.save(update_fields=['progress_percent', 'is_completed', 'completed_at', 'updated_at'])

        return f"Progress for {user.username} in {course.title}: {percent}%"

    except Exception as e:
        logger.exception(f"Error recalculating progress for user={user_id} course={course_id}")
        task_self.retry(exc=e, countdown=10)
