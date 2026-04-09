import pytest
from django.core.exceptions import ValidationError
from apps.assessments.services import AssessmentService
from apps.assessments.models import Submission

@pytest.mark.django_db
class TestAssessmentService:
    def test_submit_assessment(self, student, assessment):
        submission = AssessmentService.submit_assessment(
            user=student,
            assessment_uuid=assessment.uuid,
            answers={'1': 0}
        )
        assert Submission.objects.count() == 1
        assert submission.user == student
        assert submission.assessment == assessment
        assert submission.answers == {'1': 0}
        assert submission.status == 'PENDING'

    def test_duplicate_submission_fails(self, student, assessment):
        AssessmentService.submit_assessment(
            user=student,
            assessment_uuid=assessment.uuid,
            answers={'1': 0}
        )
        with pytest.raises(ValidationError, match="already submitted"):
            AssessmentService.submit_assessment(
                user=student,
                assessment_uuid=assessment.uuid,
                answers={'1': 0}
            )
