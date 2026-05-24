from django.db import models
from django.conf import settings

class InterviewSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    created_at = models.DateTimeField(auto_now_add=True)

    emotion_score_total = models.IntegerField(default=0.0)
    eye_score_total = models.IntegerField(default=0.0)
    frame_count = models.IntegerField(default=0.0)
    feedback = models.TextField(blank=True, null=True)

    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - Score: {self.emotion_score_total / self.frame_count}"