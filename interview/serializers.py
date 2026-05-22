from rest_framework import serializers
from .models import InterviewSession

# Serializer used for the creation of interview sessions.
class InterviewSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = ['id', 'user']
        read_only_fields = ['user']