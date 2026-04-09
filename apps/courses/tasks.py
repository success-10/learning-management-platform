from celery import shared_task
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, acks_late=True)
def warm_course_cache(self):
    """
    Periodic task: Pre-compute and cache the published course catalog.
    Scheduled via Celery Beat.
    """
    try:
        from .models import Course
        courses = list(
            Course.objects.filter(
                is_published=True
            ).select_related('instructor').prefetch_related('modules__lessons')
        )
        cache.set('published_courses_list', courses, 600)  # 10 minutes
        logger.info(f"Course cache warmed: {len(courses)} courses cached")
        return f"Cached {len(courses)} published courses"
    except Exception as e:
        logger.exception("Error warming course cache")
        self.retry(exc=e, countdown=30)
