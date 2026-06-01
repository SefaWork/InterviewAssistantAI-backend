from django.db import models
from django.conf import settings
import uuid

class CompletedInterviewSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='completed_interviews')
    created_at = models.DateTimeField(auto_now_add=True)

    emotion_score = models.FloatField(default=0)
    eye_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    feedback = models.TextField(blank=True, null=True)
    past_analysis_feedback = models.TextField(blank=True, null=True)

    class Meta:
        get_latest_by = "created_at"

class OngoingInterviewSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_sessions')

    emotion_score_total = models.IntegerField(default=0)
    eye_score_total = models.IntegerField(default=0)
    frame_count = models.IntegerField(default=0)

    elapsed_time = models.FloatField(default=0.0)