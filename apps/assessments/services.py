from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Submission, Assessment
from apps.core.events import assessment_submitted
from apps.audit_logs.services import AuditLogService


class AssessmentService:
    @staticmethod
    def submit_assessment(*, user, assessment_uuid, answers, path=None, ip=None):
        """
        Creates a submission and emits the assessment_submitted event.
        """
        assessment = Assessment.objects.get(uuid=assessment_uuid)

        if Submission.objects.filter(user=user, assessment=assessment).exists():
            raise ValidationError("Assessment already submitted.")

        with transaction.atomic():
            submission = Submission.objects.create(
                user=user,
                assessment=assessment,
                answers=answers,
                status=Submission.Status.PENDING
            )

            AuditLogService.log(
                user=user,
                action="ASSESSMENT_SUBMITTED",
                obj=assessment,
                path=path,
                ip_address=ip
            )

            transaction.on_commit(
                lambda: assessment_submitted.send(
                    sender=AssessmentService,
                    submission_id=submission.id
                )
            )

            return submission
