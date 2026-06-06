from rest_framework import serializers
from interview.models import CompletedInterviewSession
from interview.emotion_weights import EMOTION_LIST

class SessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedInterviewSession
        fields = ('id', 'created_at', 'total_score', 'duration')

class SessionDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedInterviewSession
        fields = ('id', 'created_at', 'emotion_score', 'eye_score', 'total_score', 'feedback', 'past_analysis_feedback', 'duration', *EMOTION_LIST, "unknown")
