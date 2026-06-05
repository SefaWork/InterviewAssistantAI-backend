from django.db import models
from django.conf import settings
import uuid

class CompletedInterviewSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='completed_interviews')
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=0.0)

    emotion_score = models.FloatField(default=0)
    eye_score = models.FloatField(default=0)
    total_score = models.FloatField(default=0)

    # Individual emotion distributions.
    happy = models.FloatField(default=0.0)
    sad = models.FloatField(default=0.0)
    angry = models.FloatField(default=0.0)
    disgusted = models.FloatField(default=0.0)
    shocked = models.FloatField(default=0.0)
    neutral = models.FloatField(default=0.0)
    scared = models.FloatField(default=0.0)
    unknown = models.FloatField(default=0.0)

    feedback = models.TextField(blank=True, null=True)
    past_analysis_feedback = models.TextField(blank=True, null=True)

    class Meta:
        get_latest_by = "created_at"

class OngoingInterviewSession(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='ongoing_session')

    frame_count = models.IntegerField(default=0)
    elapsed_time = models.FloatField(default=0.0)

    # Individual emotion fields.
    happy = models.IntegerField(default=0)
    sad = models.IntegerField(default=0)
    angry = models.IntegerField(default=0)
    disgusted = models.IntegerField(default=0)
    shocked = models.IntegerField(default=0)
    neutral = models.IntegerField(default=0)
    scared = models.IntegerField(default=0)

    # Other score fields.
    emotion_score_total = models.IntegerField(default=0)
    eye_score_total = models.IntegerField(default=0)
 