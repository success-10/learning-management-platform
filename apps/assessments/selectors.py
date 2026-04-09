from apps.assessments.models import Assessment, Submission
from django.db.models import QuerySet


class AssessmentSelector:
    """Read operations for assessments."""

    @staticmethod
    def get_published_assessments() -> QuerySet:
        return Assessment.objects.filter(
            lesson__module__course__is_published=True
        ).prefetch_related('questions')

    @staticmethod
    def get_assessments_for_lesson(lesson) -> QuerySet:
        return Assessment.objects.filter(
            lesson=lesson
        ).prefetch_related('questions')

    @staticmethod
    def get_user_submissions(user) -> QuerySet:
        return Submission.objects.filter(
            user=user
        ).select_related('assessment', 'assessment__lesson__module__course')

    @staticmethod
    def get_submission_by_uuid(uuid):
        return Submission.objects.select_related(
            'user', 'assessment'
        ).get(uuid=uuid)
