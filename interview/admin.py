from django.contrib import admin
from .models import InterviewSession

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'emotion_score', 'eye_contact_score')
    list_filter = ('created_at',)
    search_fields = ('user__email',)