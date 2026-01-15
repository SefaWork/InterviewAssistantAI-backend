from django.urls import path
from .views import InterviewListCreateView, AnalyzeFrameView

urlpatterns = [
    path('sessions/', InterviewListCreateView.as_view(), name='interview_sessions'),
    path('analyze/', AnalyzeFrameView.as_view(), name='analyze_frame'),
]