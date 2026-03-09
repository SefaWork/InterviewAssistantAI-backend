from rest_framework import serializers
from .models import InterviewSession

class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        
        fields = ['id', 'user', 'created_at', 'emotion_score', 'eye_contact_score', 'feedback']
        
        
        read_only_fields = ['id', 'user', 'created_at']