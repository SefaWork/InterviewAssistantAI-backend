from django.db import models
from django.conf import settings

class InterviewSession(models.Model):
   
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    emotion_score = models.FloatField(default=0.0) 
    eye_contact_score = models.FloatField(default=0.0) 
    
    
    feedback = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.user.email} - Skoru: {self.emotion_score}"