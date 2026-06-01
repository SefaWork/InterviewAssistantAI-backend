from rest_framework import serializers
from .models import OngoingInterviewSession

# Serializer used for the creation of interview sessions.
class InterviewSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OngoingInterviewSession
        fields = ['id']