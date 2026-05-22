from rest_framework import serializers
from .models import InterviewSession

# Serializer used for the creation of interview sessions.
class InterviewSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ('id', 'user', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

# DEPRECATED SERIALIZER.
class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ['id', 'user', 'created_at', 'emotion_score', 'eye_contact_score', 'feedback']
        read_only_fields = ['id', 'user', 'created_at']