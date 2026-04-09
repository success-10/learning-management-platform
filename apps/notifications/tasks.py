from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Notification
from apps.assessments.models import Submission
from apps.courses.models import Course
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, retry_backoff=True, retry_jitter=True, acks_late=True)
def send_score_notification(self, submission_id, score, passed):
    """Send notification when an assessment is scored."""
    try:
        submission = Submission.objects.select_related('user', 'assessment').get(id=submission_id)
        user = submission.user
        assessment = submission.assessment

        status_text = "PASSED" if passed else "FAILED"
        title = f"Assessment Result: {assessment.title}"
        message = (
            f"Hello {user.username},\n\n"
            f"You scored {score:.1f}% on {assessment.title}.\n"
            f"Result: {status_text}."
        )

        # Idempotency check
        if Notification.objects.filter(user=user, title=title).exists():
            return f"Notification already sent for {assessment.title}"

        # Create DB Notification
        Notification.objects.create(user=user, title=title, message=message)

        # Send Email (Console in dev, SMTP in prod)
        send_mail(
            subject=title,
            message=message,
            from_email='system@eduflow.com',
            recipient_list=[user.email],
            fail_silently=True
        )

        return f"Score notification sent to {user.email}"

    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found for notification")
        return f"Submission {submission_id} not found"
    except Exception as e:
        logger.exception(f"Error sending score notification for submission {submission_id}")
        self.retry(exc=e, countdown=10)


@shared_task(bind=True, max_retries=3, default_retry_delay=30, retry_backoff=True, retry_jitter=True, acks_late=True)
def send_enrollment_notification(self, student_id, course_id):
    """Send notification when a student enrolls in a course."""
    try:
        User = get_user_model()
        user = User.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)

        title = f"Enrolled: {course.title}"
        message = (
            f"Hello {user.username},\n\n"
            f"You have been successfully enrolled in \"{course.title}\".\n"
            f"Start learning now!"
        )

        # Idempotency check
        if Notification.objects.filter(user=user, title=title).exists():
            return f"Enrollment notification already sent for {course.title}"

        Notification.objects.create(user=user, title=title, message=message)

        send_mail(
            subject=title,
            message=message,
            from_email='system@eduflow.com',
            recipient_list=[user.email],
            fail_silently=True
        )

        return f"Enrollment notification sent to {user.email}"

    except Exception as e:
        logger.exception(f"Error sending enrollment notification: student={student_id} course={course_id}")
        self.retry(exc=e, countdown=10)
