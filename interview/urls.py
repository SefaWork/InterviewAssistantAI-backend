from django.urls import path
from .views import InterviewListCreateView

urlpatterns = [
    path('sessions/', InterviewListCreateView.as_view(), name='interview_sessions'),
]