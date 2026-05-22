from rest_framework import serializers
from interview.models import InterviewSession

class SessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ('id', 'created_at')

class SessionDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ('id', 'created_at', 'emotion_score', 'eye_contact_score')