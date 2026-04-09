from celery import shared_task
from django.db import transaction
from .models import Submission, Question
from apps.core.events import score_calculated
from apps.audit_logs.services import AuditLogService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, retry_backoff=True, retry_jitter=True, acks_late=True)
def calculate_score(self, submission_id):
    try:
        submission = Submission.objects.select_related(
            'user', 'assessment__lesson__module__course'
        ).get(id=submission_id)

        # Idempotency check
        if submission.status == Submission.Status.SCORED:
            return f"Submission {submission_id} already scored."

        logger.info(f"Scoring submission {submission_id}")

        questions = submission.assessment.questions.all()
        total_points = sum(q.points for q in questions)
        earned_points = 0

        user_answers = submission.answers  # Dict {str(question_id): int(option_index)}

        for question in questions:
            # Keys in JSON might be strings
            qid_str = str(question.id)
            if qid_str in user_answers:
                user_choice = user_answers[qid_str]
                if user_choice == question.correct_option_index:
                    earned_points += question.points

        score_percent = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = score_percent >= submission.assessment.passing_score

        with transaction.atomic():
            submission.score = score_percent
            submission.passed = passed
            submission.status = Submission.Status.SCORED
            submission.save(update_fields=['score', 'passed', 'status'])

            AuditLogService.log(
                user=submission.user,
                action="ASSESSMENT_SCORED",
                obj=submission.assessment,
            )

            # Emit ScoreCalculated event after commit
            course = submission.assessment.lesson.module.course

            def emit_scored():
                score_calculated.send(
                    sender=Submission,
                    submission_id=submission.id,
                    user_id=submission.user_id,
                    course_id=course.id,
                    assessment_id=submission.assessment_id,
                    score=score_percent,
                    passed=passed
                )
            transaction.on_commit(emit_scored)

        return f"Scored {submission_id}: {score_percent}%"

    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found.")
    except Exception as e:
        logger.exception(f"Error scoring submission {submission_id}")
        self.retry(exc=e, countdown=10)
