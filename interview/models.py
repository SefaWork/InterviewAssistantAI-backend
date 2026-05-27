from django.db import models
from django.conf import settings
import uuid

class InterviewSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    created_at = models.DateTimeField(auto_now_add=True)

    emotion_score_total = models.IntegerField(default=0.0)
    eye_score_total = models.IntegerField(default=0.0)
    frame_count = models.IntegerField(default=0.0)

    completed = models.BooleanField(default=False)

    # Feedback.
    feedback = models.TextField(blank=True, null=True)

    # Feedback compared to past sessions.
    past_analysis_feedback = models.TextField(blank=True, null=True)

    class Meta:
        get_latest_by = "created_at"

    def __str__(self):
        return f"{self.user.email} - Score: {self.emotion_score_total / self.frame_count}"