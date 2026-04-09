from rest_framework import serializers
from apps.assessments.models import Assessment, Question, Submission


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('uuid', 'text', 'options', 'points', 'order')


class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = ('uuid', 'title', 'description', 'passing_score', 'questions')


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('uuid', 'assessment', 'status', 'score', 'passed', 'created_at')
        read_only_fields = ('status', 'score', 'passed', 'created_at')


class CreateSubmissionSerializer(serializers.Serializer):
    assessment_uuid = serializers.UUIDField()
    answers = serializers.DictField(
        child=serializers.IntegerField(min_value=0),
        help_text="{question_id: option_index}"
    )

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("Answers cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Too many answers submitted.")
        return value
