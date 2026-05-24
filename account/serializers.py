from rest_framework import serializers
from interview.models import InterviewSession

class SessionListSerializer(serializers.ModelSerializer):
    total_avg = serializers.SerializerMethodField()

    class Meta:
        model = InterviewSession
        fields = ('id', 'created_at', 'total_avg')
    
    def get_total_avg(self, obj):
        if obj.frame_count == 0:
            return 0

        return round((obj.emotion_score_total + obj.eye_score_total) / (obj.frame_count * 2), 1)

class SessionDisplaySerializer(serializers.ModelSerializer):
    emotion_avg = serializers.SerializerMethodField()
    eye_avg = serializers.SerializerMethodField()
    total_avg = serializers.SerializerMethodField()

    class Meta:
        model = InterviewSession
        fields = ('id', 'created_at', 'emotion_avg', 'eye_avg', 'total_avg', 'feedback')

    def get_emotion_avg(self, obj):
        if obj.frame_count == 0:
            return 0
        
        return round(obj.emotion_score_total / obj.frame_count, 1)
    
    def get_eye_avg(self, obj):
        if obj.frame_count == 0:
            return 0
        
        return round(obj.eye_score_total / obj.frame_count, 1)
    
    def get_total_avg(self, obj):
        if obj.frame_count == 0:
            return 0

        return round((obj.emotion_score_total + obj.eye_score_total) / (obj.frame_count * 2), 1)
