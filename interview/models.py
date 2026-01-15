from django.db import models
from django.conf import settings

class InterviewSession(models.Model):
   
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    
    start_time = models.DateTimeField(auto_now_add=True)
    
   
    eye_contact_score = models.FloatField(default=0.0)
    expression_score = models.FloatField(default=0.0)
    
    
    feedback_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.start_time.strftime('%d-%m-%Y')}"